import asyncio
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)
from playwright.async_api import async_playwright

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token provided
BOT_TOKEN = "8810991883:AAHToP4c764L48eOQ_IwC519n5-0bzvYoUA"
HOTSTAR_URL = "https://www.hotstar.com/in/payment/checkout?billing_frequency=1&billing_interval_unit=MONTHS&browser_url=%2Fin%2Fpaywall%2Fv2&dr_flow=true&failed_pc_entitlement_context=%7B%22max_concurrent_signins%22%3A%222%22%7D&failed_pc_entitlement_required=%5B%22max_concurrent_signins%22%5D&family=HotstarSuper&packId=HotstarPremium.IN.Month.299&pack_id=HotstarPremium.IN.Month.299&planDuration=MONTHS&planFamily=HotstarPremiumSmp&planFrequency=1&promo=UPP_1MP100&source=dr"

# Conversation states
GET_NUMBER, GET_OTP = range(2)

# Global multi-user session dictionary store
user_sessions = {}

async def safe_close_session(chat_id: int):
    """Safely terminates browser resources for a specific user."""
    if chat_id in user_sessions:
        try:
            session = user_sessions[chat_id]
            if "browser" in session and session["browser"]:
                await session["browser"].close()
            if "playwright" in session and session["playwright"]:
                await session["playwright"].stop()
        except Exception as e:
            logger.error(f"Error closing session for {chat_id}: {e}")
        finally:
            user_sessions.pop(chat_id, None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Multi-user start command with clean UI."""
    chat_id = update.effective_chat.id
    await safe_close_session(chat_id)  # Clear any stale session if present

    keyboard = [[InlineKeyboardButton("🚫 Cancel Process", callback_data="cancel_flow")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🔥 **Hotstar Premium ₹1 Instant Bot** 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚡ **Fast • Automatic • Multi-User Ready**\n\n"
        "📲 Please enter your **10-Digit Mobile Number** (without +91):\n"
        "👉 *Example:* `9868886810`"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    return GET_NUMBER

async def receive_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes phone input and launches dedicated browser instance for the specific user."""
    chat_id = update.effective_chat.id
    mobile_number = update.message.text.strip()
    
    if not mobile_number.isdigit() or len(mobile_number) != 10:
        await update.message.reply_text(
            "⚠️ **Invalid Mobile Number!**\nPlease provide a valid 10-digit Indian phone number without +91.",
            parse_mode="Markdown"
        )
        return GET_NUMBER

    status_msg = await update.message.reply_text("🚀 *Connecting to Hotstar Checkout...*", parse_mode="Markdown")

    try:
        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context_browser = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context_browser.new_page()

        # Fast page loading
        await page.goto(HOTSTAR_URL, timeout=45000, wait_until="domcontentloaded")
        
        # Enter phone number
        phone_input = page.locator("input[data-testid='signup-form-submit-button'], input._2fyaLvoy3ihArVClDsg1Wk").first
        await phone_input.fill(mobile_number)
        
        # Click Get OTP
        get_otp_btn = page.locator("button[data-testid='signup-form-submit-button']")
        await get_otp_btn.click()
        
        # Save isolated user session
        user_sessions[chat_id] = {
            "playwright": p,
            "browser": browser,
            "page": page,
            "mobile": mobile_number,
            "payment_success": False
        }

        keyboard = [[InlineKeyboardButton("❌ Cancel Session", callback_data="cancel_flow")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await status_msg.edit_text(
            f"✅ **OTP Sent Successfully!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 **Mobile:** `+91 {mobile_number}`\n\n"
            f"📩 Please enter the **4-digit OTP** sent to your phone:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return GET_OTP

    except Exception as e:
        logger.error(f"Error in receive_number for user {chat_id}: {e}")
        await safe_close_session(chat_id)
        await status_msg.edit_text(
            f"💥 **Automation Error:** `{str(e)}`\n\nType /start to try again.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

async def receive_otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verifies OTP, captures QR code, monitors payment status API, and returns final success URL."""
    chat_id = update.effective_chat.id
    otp = update.message.text.strip()

    if chat_id not in user_sessions:
        await update.message.reply_text("⏰ **Session Expired!**\nPlease send /start to begin a new process.", parse_mode="Markdown")
        return ConversationHandler.END

    session = user_sessions[chat_id]
    page = session["page"]
    mobile_number = session["mobile"]

    # Network response listener for payment completion
    async def handle_response(response):
        if "payment/status" in response.url:
            try:
                data = await response.json()
                if "active on" in str(data) or "Congratulations" in str(data) or "success" in str(data).lower():
                    session["payment_success"] = True
            except Exception:
                pass

    page.on("response", handle_response)

    status_msg = await update.message.reply_text("🔄 *Verifying OTP & Preparing QR Code...*", parse_mode="Markdown")

    try:
        # Fill OTP inputs individually
        for i, digit in enumerate(otp[:4]):
            otp_box = page.locator(f"input[data-testid='id-{i}']")
            await otp_box.click()
            await otp_box.fill(digit)

        # Submit OTP
        continue_btn = page.locator("button[data-testid='otp-form-submit-button']")
        await continue_btn.click()

        await page.wait_for_timeout(3000)

        # Check for incorrect OTP message
        error_locator = page.locator("text=Incorrect OTP entered. Please enter again.")
        if await error_locator.count() > 0:
            await status_msg.edit_text(
                "❌ **Incorrect OTP Entered!**\n\nSession terminated for security. Please send /start to try again.",
                parse_mode="Markdown"
            )
            await safe_close_session(chat_id)
            return ConversationHandler.END

        # Click "Show QR Code" button
        try:
            qr_btn = page.locator("button:has-text('Show QR Code')")
            await qr_btn.click(timeout=8000)
            await page.wait_for_timeout(2500)
        except Exception as qr_err:
            logger.warning(f"QR Click exception for {chat_id}: {qr_err}")

        # Send QR screenshot
        screenshot_path = Path.cwd() / f"qr_{chat_id}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        await status_msg.delete()
        with open(screenshot_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=(
                    "📸 **Scan QR Code to Complete Payment**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💰 **Amount:** ₹1\n"
                    "⏳ *Waiting for your payment completion...*"
                ),
                parse_mode="Markdown"
            )

        if screenshot_path.exists():
            screenshot_path.unlink()

        # Monitor payment status loop (up to 3 minutes)
        await update.message.reply_text("⏳ *Tracking payment status...*", parse_mode="Markdown")
        
        for _ in range(36):
            await asyncio.sleep(5)
            if session.get("payment_success"):
                break

        # Capture final success screen & redirect URL params
        current_url = page.url
        success_screenshot = Path.cwd() / f"success_{chat_id}.png"
        await page.screenshot(path=str(success_screenshot), full_page=True)

        with open(success_screenshot, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=(
                    "🎉 **Payment Successful & Subscription Active!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📱 **Account:** `{mobile_number}`\n\n"
                    f"🔗 **Redirect URL:**\n`{current_url}`"
                ),
                parse_mode="Markdown"
            )

        if success_screenshot.exists():
            success_screenshot.unlink()

        await safe_close_session(chat_id)

    except Exception as e:
        logger.error(f"Error processing OTP for {chat_id}: {e}")
        await update.message.reply_text(f"❌ **Error:** `{str(e)}`\n\nPlease /start again.", parse_mode="Markdown")
        await safe_close_session(chat_id)
        return ConversationHandler.END

    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enhanced /cancel command handler."""
    chat_id = update.effective_chat.id
    await safe_close_session(chat_id)
    
    cancel_text = (
        "🛑 **Process Cancelled Successfully!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "All active sessions and browser resources have been closed.\n\n"
        "👇 Send /start to begin a new activation."
    )
    await update.message.reply_text(cancel_text, parse_mode="Markdown")
    return ConversationHandler.END

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback handler for inline buttons."""
    query = update.callback_query
    chat_id = update.effective_chat.id
    await query.answer()

    if query.data == "cancel_flow":
        await safe_close_session(chat_id)
        await query.message.edit_text(
            "🛑 **Process Cancelled!**\n\nSend /start anytime to begin again.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

def main():
    """Run bot with multi-user isolation."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_number),
                CallbackQueryHandler(button_callback, pattern="^cancel_flow$")
            ],
            GET_OTP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_otp),
                CallbackQueryHandler(button_callback, pattern="^cancel_flow$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CallbackQueryHandler(button_callback, pattern="^cancel_flow$")
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Multi-User High-Speed Hotstar Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main()
