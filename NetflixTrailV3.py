import asyncio
import json
import logging
import secrets
import string
from pathlib import Path
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters, ConversationHandler,
)
from playwright.async_api import async_playwright

# ---------------- LOGGING ----------------
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# ---------------- CONFIG ----------------
BOT_TOKEN = "8810991883:AAHToP4c764L48eOQ_IwC519n5-0bzvYoUA"
ADMIN_IDS = [8295155770]  # Owner(s) — unlimited balance

HOTSTAR_PREMIUM_URL = (
    "https://www.hotstar.com/in/payment/checkout?billing_frequency=1"
    "&billing_interval_unit=MONTHS&browser_url=%2Fin%2Fpaywall%2Fv2&dr_flow=true"
    "&failed_pc_entitlement_context=%7B%22max_concurrent_signins%22%3A%222%22%7D"
    "&failed_pc_entitlement_required=%5B%22max_concurrent_signins%22%5D"
    "&family=HotstarSuper&packId=HotstarPremium.IN.Month.299"
    "&pack_id=HotstarPremium.IN.Month.299&planDuration=MONTHS"
    "&planFamily=HotstarPremiumSmp&planFrequency=1&promo=UPP_1MP100&source=dr"
)

# ---------------- STORAGE ----------------
DATA_DIR = Path.cwd() / "data"
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
KEYS_FILE = DATA_DIR / "keys.json"

_users_cache = None
_keys_cache = None

GET_NUMBER, GET_OTP = range(2)
user_sessions = {}


def load_users() -> dict:
    global _users_cache
    if _users_cache is None:
        if USERS_FILE.exists():
            try:
                _users_cache = json.loads(USERS_FILE.read_text(encoding="utf-8"))
            except Exception:
                _users_cache = {}
        else:
            _users_cache = {}
    return _users_cache


def save_users():
    if _users_cache is not None:
        USERS_FILE.write_text(json.dumps(_users_cache, indent=2), encoding="utf-8")


def load_keys() -> dict:
    global _keys_cache
    if _keys_cache is None:
        if KEYS_FILE.exists():
            try:
                _keys_cache = json.loads(KEYS_FILE.read_text(encoding="utf-8"))
            except Exception:
                _keys_cache = {}
        else:
            _keys_cache = {}
    return _keys_cache


def save_keys():
    if _keys_cache is not None:
        KEYS_FILE.write_text(json.dumps(_keys_cache, indent=2), encoding="utf-8")


def get_user(user) -> dict:
    users = load_users()
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "id": user.id,
            "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
            "username": user.username or "",
            "balance": 0,
            "total_used": 0,
            "total_success": 0,
            "total_incorrect_otp": 0,
            "total_payment_stuck": 0,
            "total_not_valid": 0,
            "banned": False,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_users()
    else:
        users[uid]["name"] = f"{user.first_name or ''} {user.last_name or ''}".strip()
        users[uid]["username"] = user.username or ""
        save_users()
    return users[uid]


def update_user(uid, **kwargs):
    users = load_users()
    uid = str(uid)
    if uid in users:
        users[uid].update(kwargs)
        save_users()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def balance_display(user_id: int, balance: int) -> str:
    """Show ∞ for admins."""
    return "∞ (Owner)" if is_admin(user_id) else str(balance)


def has_balance(user_id: int, balance: int) -> bool:
    """Admins always have balance. Users need > 0."""
    if is_admin(user_id):
        return True
    return balance > 0


def generate_key_code(length: int = 16) -> str:
    alphabet = string.ascii_uppercase + string.digits
    keys = load_keys()
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if code not in keys:
            return code


# ---------------- KEYBOARDS ----------------
def main_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton("🚀 Start Hotstar Flow", callback_data="menu_start")],
        [
            InlineKeyboardButton("📊 My Info", callback_data="menu_info"),
            InlineKeyboardButton("🔑 Redeem Key", callback_data="menu_redeem"),
        ],
        [
            InlineKeyboardButton("💳 Balance", callback_data="menu_balance"),
            InlineKeyboardButton("ℹ️ Help", callback_data="menu_help"),
        ],
    ]
    if is_admin(user_id):
        kb.append([InlineKeyboardButton("🛠 Admin Panel", callback_data="menu_admin")])
    return InlineKeyboardMarkup(kb)


def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📈 Stats", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Users", callback_data="admin_users"),
        ],
        [InlineKeyboardButton("🔑 Key Help", callback_data="admin_keyhelp")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_home")],
    ])


def back_kb(target: str = "menu_home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=target)]])


# ---------------- SAFE SESSION CLOSE ----------------
async def safe_close_session(chat_id: int):
    session = user_sessions.pop(chat_id, None)
    if not session:
        return
    try:
        if session.get("browser"):
            await session["browser"].close()
    except Exception:
        pass
    try:
        if session.get("playwright"):
            await session["playwright"].stop()
    except Exception:
        pass


# ---------------- MENUS ----------------
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    user = update.effective_user
    u = get_user(user)
    bal = balance_display(user.id, u["balance"])
    text = (
        f"👋 Welcome, **{user.first_name}**!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 **Hotstar Premium ₹1 Instant Bot** 🔥\n\n"
        f"💳 **Balance:** `{bal}`\n"
        f"✅ **Success:** `{u['total_success']}`\n\n"
        "💡 *Points are deducted only on successful activation.*\n\n"
        "Use the buttons below 👇"
    )
    kb = main_menu_kb(user.id)
    if edit and update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            try:
                await update.callback_query.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")
            except Exception:
                pass
    else:
        await update.effective_message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = get_user(user)
    if u.get("banned") and not is_admin(user.id):
        await update.message.reply_text("⛔ **Access Denied:** You are banned.", parse_mode="Markdown")
        return
    await show_main_menu(update, context, edit=False)


# ---------------- HELP ----------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 **Help & Commands**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**👤 User Commands**\n"
        "• /start – Open main menu\n"
        "• /code `<KEY>` – Redeem a key to get balance\n"
        "• /info – Show your account details\n"
        "• /balance – Show your balance\n"
        "• /help – Show this help\n"
        "• /cancel – Cancel current flow\n\n"
        "💡 **Note:** Points are deducted **only on successful activation**, not on flow start.\n\n"
        "**🛠 Admin Commands**\n"
        "• /gen `<count> <uses> <days>` – Generate keys\n"
        "• /addbal `<user_id> <amount>` – Add balance\n"
        "• /removebal `<user_id> <amount>` – Remove balance\n"
        "• /resetbal `<user_id>` – Set balance to 0\n"
        "• /ban `<user_id>` – Ban user\n"
        "• /unban `<user_id>` – Unban user\n"
        "• /stats – Global bot stats\n"
        "• /user `<user_id>` – View specific user\n"
        "• /allusers – List all users\n"
        "• /keys – List active keys\n"
    )
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=back_kb(), parse_mode="Markdown")
        except Exception:
            pass
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = get_user(user)
    bal = balance_display(user.id, u["balance"])
    role = "👑 Owner" if is_admin(user.id) else "👤 User"
    text = (
        "📊 **Your Account Info**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** {u['name'] or 'N/A'}\n"
        f"🔗 **Username:** @{u['username'] if u['username'] else 'N/A'}\n"
        f"🆔 **User ID:** `{u['id']}`\n"
        f"🎖 **Role:** {role}\n"
        f"📅 **Joined:** {u['joined']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 **Balance:** `{bal}`\n"
        f"🔢 **Total Used:** `{u['total_used']}`\n"
        f"✅ **Success:** `{u['total_success']}`\n"
        f"❌ **Incorrect OTP:** `{u['total_incorrect_otp']}`\n"
        f"⏳ **Payment Stuck:** `{u['total_payment_stuck']}`\n"
        f"🚫 **Offer Not Valid:** `{u['total_not_valid']}`\n"
    )
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=back_kb(), parse_mode="Markdown")
        except Exception:
            pass
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = get_user(user)
    bal = balance_display(user.id, u["balance"])
    text = f"💳 **Balance:** `{bal}` uses\n\n💡 *Deducted only on success.*"
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=back_kb(), parse_mode="Markdown")
        except Exception:
            pass
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


# ---------------- KEY REDEEM ----------------
async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = get_user(user)
    if u.get("banned") and not is_admin(user.id):
        await update.message.reply_text("⛔ You are banned.", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text(
            "🔑 **Usage:** `/code YOURKEY`\nExample: `/code ABC123XYZ`",
            parse_mode="Markdown"
        )
        return

    code = context.args[0].strip().upper()
    keys = load_keys()
    if code not in keys:
        await update.message.reply_text("❌ **Invalid key.**", parse_mode="Markdown")
        return

    key_data = keys[code]
    if key_data.get("redeemed_by"):
        await update.message.reply_text("❌ **Key already used.**", parse_mode="Markdown")
        return

    expires = datetime.fromisoformat(key_data["expires"])
    if datetime.now() > expires:
        await update.message.reply_text("❌ **Key expired.**", parse_mode="Markdown")
        return

    uses = int(key_data["uses"])
    keys[code]["redeemed_by"] = user.id
    keys[code]["redeemed_at"] = datetime.now().isoformat()
    save_keys()

    u["balance"] = u.get("balance", 0) + uses
    update_user(user.id, balance=u["balance"])

    await update.message.reply_text(
        f"✅ **Key Redeemed Successfully!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 **Key:** `{code}`\n"
        f"➕ **Added:** `{uses}` uses\n"
        f"💳 **New Balance:** `{u['balance']}` uses",
        parse_mode="Markdown"
    )


# ---------------- ADMIN: KEY GEN ----------------
async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 3:
        await update.message.reply_text(
            "🛠 **Usage:** `/gen <count> <uses> <days>`\n"
            "Example: `/gen 5 6 1` → 5 keys, 6 uses each, valid 1 day",
            parse_mode="Markdown"
        )
        return
    try:
        count = int(context.args[0])
        uses = int(context.args[1])
        days = int(context.args[2])
    except ValueError:
        await update.message.reply_text("❌ Invalid numbers.")
        return
    if count <= 0 or count > 100 or uses <= 0 or days <= 0:
        await update.message.reply_text("❌ Range error (1-100 keys).")
        return

    keys = load_keys()
    created = datetime.now()
    expires = created + timedelta(days=days)
    new_codes = []
    for _ in range(count):
        code = generate_key_code()
        keys[code] = {
            "uses": uses,
            "days": days,
            "created": created.isoformat(),
            "expires": expires.isoformat(),
            "redeemed_by": None,
            "redeemed_at": None,
        }
        new_codes.append(code)
    save_keys()

    body = "\n".join(f"`{c}`" for c in new_codes)
    await update.message.reply_text(
        f"✅ **{count} Keys Generated**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔢 **Uses/Key:** `{uses}`\n"
        f"📅 **Valid:** `{days}` day(s)\n"
        f"⏰ **Expires:** `{expires.strftime('%Y-%m-%d %H:%M')}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{body}",
        parse_mode="Markdown"
    )


# ---------------- ADMIN: BALANCE ----------------
async def addbal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/addbal <user_id> <amount>`", parse_mode="Markdown")
        return
    try:
        uid = str(int(context.args[0]))
        amt = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid arguments.")
        return
    users = load_users()
    if uid not in users:
        await update.message.reply_text("❌ User not found.")
        return
    users[uid]["balance"] = users[uid].get("balance", 0) + amt
    save_users()
    await update.message.reply_text(
        f"✅ Added `{amt}` to `{uid}`. New balance: `{users[uid]['balance']}`",
        parse_mode="Markdown"
    )


async def removebal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/removebal <user_id> <amount>`", parse_mode="Markdown")
        return
    try:
        uid = str(int(context.args[0]))
        amt = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid arguments.")
        return
    users = load_users()
    if uid not in users:
        await update.message.reply_text("❌ User not found.")
        return
    users[uid]["balance"] = max(0, users[uid].get("balance", 0) - amt)
    save_users()
    await update.message.reply_text(
        f"✅ Removed `{amt}` from `{uid}`. New balance: `{users[uid]['balance']}`",
        parse_mode="Markdown"
    )


async def resetbal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/resetbal <user_id>`", parse_mode="Markdown")
        return
    uid = str(context.args[0])
    users = load_users()
    if uid not in users:
        await update.message.reply_text("❌ User not found.")
        return
    users[uid]["balance"] = 0
    save_users()
    await update.message.reply_text(f"✅ Balance reset for `{uid}`.", parse_mode="Markdown")


# ---------------- ADMIN: BAN / UNBAN ----------------
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/ban <user_id>`", parse_mode="Markdown")
        return
    uid = str(context.args[0])
    users = load_users()
    if uid not in users:
        users[uid] = {"id": int(uid), "name": "", "username": "", "balance": 0,
                      "total_used": 0, "total_success": 0, "total_incorrect_otp": 0,
                      "total_payment_stuck": 0, "total_not_valid": 0,
                      "banned": True, "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    else:
        users[uid]["banned"] = True
    save_users()
    await update.message.reply_text(f"⛔ Banned `{uid}`.", parse_mode="Markdown")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/unban <user_id>`", parse_mode="Markdown")
        return
    uid = str(context.args[0])
    users = load_users()
    if uid in users:
        users[uid]["banned"] = False
        save_users()
        await update.message.reply_text(f"✅ Unbanned `{uid}`.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ User not found.")


# ---------------- ADMIN: STATS ----------------
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    users = load_users()
    keys = load_keys()
    total = len(users)
    banned = sum(1 for u in users.values() if u.get("banned"))
    total_bal = sum(u.get("balance", 0) for u in users.values())
    total_used = sum(u.get("total_used", 0) for u in users.values())
    total_succ = sum(u.get("total_success", 0) for u in users.values())
    total_otp = sum(u.get("total_incorrect_otp", 0) for u in users.values())
    total_stuck = sum(u.get("total_payment_stuck", 0) for u in users.values())
    total_inv = sum(u.get("total_not_valid", 0) for u in users.values())
    total_keys = len(keys)
    used_keys = sum(1 for k in keys.values() if k.get("redeemed_by"))

    text = (
        "📈 **Global Bot Stats**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **Users:** `{total}`\n"
        f"⛔ **Banned:** `{banned}`\n"
        f"💳 **Total Balance (all users):** `{total_bal}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔢 **Total Used:** `{total_used}`\n"
        f"✅ **Success:** `{total_succ}`\n"
        f"❌ **Incorrect OTP:** `{total_otp}`\n"
        f"⏳ **Payment Stuck:** `{total_stuck}`\n"
        f"🚫 **Offer Not Valid:** `{total_inv}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 **Keys:** `{total_keys}` (used: `{used_keys}`)"
    )
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=back_kb("menu_admin"), parse_mode="Markdown")
        except Exception:
            pass
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/user <user_id>`", parse_mode="Markdown")
        return
    uid = str(context.args[0])
    users = load_users()
    if uid not in users:
        await update.message.reply_text("❌ User not found.")
        return
    u = users[uid]
    role = "👑 Owner" if int(uid) in ADMIN_IDS else "👤 User"
    text = (
        f"👤 **User Info**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**Name:** {u.get('name') or 'N/A'}\n"
        f"**Username:** @{u.get('username') or 'N/A'}\n"
        f"**ID:** `{u.get('id')}`\n"
        f"**Role:** {role}\n"
        f"**Banned:** `{u.get('banned')}`\n"
        f"**Joined:** {u.get('joined')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 **Balance:** `{u.get('balance', 0)}`\n"
        f"🔢 **Total Used:** `{u.get('total_used', 0)}`\n"
        f"✅ **Success:** `{u.get('total_success', 0)}`\n"
        f"❌ **Incorrect OTP:** `{u.get('total_incorrect_otp', 0)}`\n"
        f"⏳ **Payment Stuck:** `{u.get('total_payment_stuck', 0)}`\n"
        f"🚫 **Offer Not Valid:** `{u.get('total_not_valid', 0)}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def allusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    users = load_users()
    if not users:
        await update.message.reply_text("No users yet.")
        return
    lines = []
    for uid, u in list(users.items())[:60]:
        lines.append(f"`{uid}` | {u.get('name', '')[:15]} | 💳 {u.get('balance', 0)} | ✅ {u.get('total_success', 0)}")
    text = "👥 **Users** (first 60)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="Markdown")


async def keys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    keys = load_keys()
    active = [(k, v) for k, v in keys.items() if not v.get("redeemed_by") and datetime.now() < datetime.fromisoformat(v["expires"])]
    if not active:
        await update.message.reply_text("No active keys.")
        return
    lines = [f"`{k}` | uses:{v['uses']} | exp:{datetime.fromisoformat(v['expires']).strftime('%m-%d %H:%M')}" for k, v in active[:50]]
    text = f"🔑 **Active Keys** ({len(active)})\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="Markdown")


# ---------------- FLOW: START ----------------
async def start_flow_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    u = get_user(user)

    if u.get("banned") and not is_admin(user.id):
        try:
            await query.message.edit_text("⛔ You are banned.", reply_markup=back_kb())
        except Exception:
            pass
        return ConversationHandler.END

    # Owner bypass — no balance check
    if not has_balance(user.id, u.get("balance", 0)):
        try:
            await query.message.edit_text(
                "💳 **Insufficient Balance!**\n\n"
                "You need balance to use this bot.\n"
                "Use `/code <KEY>` to redeem a key.\n\n"
                "💡 *Points are deducted only on successful activation.*",
                reply_markup=back_kb(), parse_mode="Markdown"
            )
        except Exception:
            pass
        return ConversationHandler.END

    await safe_close_session(update.effective_chat.id)
    kb = [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel_flow")]]
    bal = balance_display(user.id, u["balance"])
    try:
        await query.message.edit_text(
            f"📲 **Enter your 10-digit Mobile Number** (without +91):\n\n"
            f"👉 Example: `9868886810`\n"
            f"💳 Balance: `{bal}`\n\n"
            f"💡 *Points deducted only on SUCCESS.*",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown"
        )
    except Exception:
        pass
    return GET_NUMBER


async def receive_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    user = update.effective_user
    mobile = update.message.text.strip()

    if not mobile.isdigit() or len(mobile) != 10:
        await update.message.reply_text("⚠️ **Invalid Mobile Number!** Send 10 digits.", parse_mode="Markdown")
        return GET_NUMBER

    u = get_user(user)
    if not has_balance(user.id, u.get("balance", 0)):
        await update.message.reply_text("💳 **Balance empty.** Redeem a key with /code.", parse_mode="Markdown")
        return ConversationHandler.END

    status_msg = await update.message.reply_text("🚀 *Connecting to Hotstar...*", parse_mode="Markdown")

    p = None
    browser = None
    try:
        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-setuid-sandbox",
                "--disable-accelerated-2d-canvas",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )

        async def block_heavy(route):
            try:
                rtype = route.request.resource_type
                url = route.request.url.lower()
                if rtype in ("image", "font", "media") or \
                   any(x in url for x in ["google-analytics", "doubleclick",
                                          "facebook.net", "hotjar", "segment.io",
                                          "scorecardresearch", "adservice"]):
                    await route.abort()
                else:
                    await route.continue_()
            except Exception:
                try:
                    await route.continue_()
                except Exception:
                    pass

        page = await ctx.new_page()
        await page.route("**/*", block_heavy)
        page.set_default_timeout(90000)
        page.set_default_navigation_timeout(90000)

        loaded = False
        last_err = None
        for attempt in range(2):
            try:
                await page.goto(HOTSTAR_PREMIUM_URL, timeout=90000, wait_until="commit")
                await page.wait_for_timeout(4500)
                loaded = True
                break
            except Exception as ge:
                last_err = ge
                logger.warning(f"goto attempt {attempt+1} failed: {ge}")
                await page.wait_for_timeout(2000)

        if not loaded:
            raise Exception(f"Page load failed: {str(last_err)[:120]}")

        selectors = [
            "input[data-testid='signup-form-submit-button']",
            "input._2fyaLvoy3ihArVClDsg1Wk",
            "input[type='tel']",
            "input[type='number']",
            "input[inputmode='numeric']",
            "input[placeholder*='mobile' i]",
            "input[placeholder*='phone' i]",
            "input[aria-label*='mobile' i]",
        ]

        phone_input = None
        for sel in selectors:
            try:
                loc = page.locator(sel).first
                if await loc.count() > 0:
                    await loc.wait_for(state="visible", timeout=15000)
                    phone_input = loc
                    break
            except Exception:
                continue

        if phone_input is None:
            try:
                all_inputs = page.locator("input")
                n = await all_inputs.count()
                for i in range(n):
                    inp = all_inputs.nth(i)
                    try:
                        typ = await inp.get_attribute("type") or ""
                        if typ in ("text", "tel", "number", ""):
                            if await inp.is_visible():
                                phone_input = inp
                                break
                    except Exception:
                        continue
            except Exception:
                pass

        if phone_input is None:
            dbg = Path.cwd() / f"debug_{chat_id}.png"
            try:
                await page.screenshot(path=str(dbg), full_page=True)
            except Exception:
                pass
            raise Exception("Phone input not found — site layout may have changed.")

        try:
            await phone_input.click(timeout=10000)
        except Exception:
            pass
        try:
            await phone_input.fill("")
        except Exception:
            pass
        await phone_input.type(mobile, delay=40)

        otp_clicked = False
        otp_btn_selectors = [
            "button[data-testid='signup-form-submit-button']",
            "button:has-text('Get OTP')",
            "button:has-text('GET OTP')",
            "button:has-text('Continue')",
            "button[type='submit']",
        ]
        for sel in otp_btn_selectors:
            try:
                btn = page.locator(sel).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click(timeout=10000)
                    otp_clicked = True
                    break
            except Exception:
                continue

        if not otp_clicked:
            try:
                await phone_input.press("Enter")
            except Exception:
                pass

        # Wait for OTP screen
        for _ in range(20):
            await page.wait_for_timeout(1000)
            found = False
            for sel in ["input[data-testid='id-0']", "input[data-testid='otp-input']",
                        "input[autocomplete='one-time-code']"]:
                try:
                    if await page.locator(sel).first.count() > 0:
                        found = True
                        break
                except Exception:
                    continue
            if found:
                break
            try:
                if await page.locator("text=User not eligible").count() > 0 or \
                   await page.locator("text=already subscribed").count() > 0:
                    break
            except Exception:
                pass

        user_sessions[chat_id] = {
            "playwright": p, "browser": browser, "page": page,
            "mobile": mobile, "payment_success": False,
            "success_event": asyncio.Event(),
            "user_id": user.id,
            "charged": False,
        }

        # Do NOT deduct balance here — only on success

        kb = [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel_flow")]]
        bal = balance_display(user.id, u["balance"])
        await status_msg.edit_text(
            f"✅ **OTP Sent!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 `+91 {mobile}`\n"
            f"💳 Balance: `{bal}`\n\n"
            f"📩 Enter the **4-digit OTP**:\n\n"
            f"💡 *1 point will be deducted on SUCCESS.*",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown"
        )
        return GET_OTP

    except Exception as e:
        logger.error(f"receive_number error: {e}")
        try:
            if browser:
                await browser.close()
        except Exception:
            pass
        try:
            if p:
                await p.stop()
        except Exception:
            pass

        err = str(e)
        if "Timeout" in err or "timed out" in err.lower():
            hint = "\n\n💡 *Hotstar is slow right now. Please try again in 30 seconds.*"
        elif "Phone input not found" in err:
            hint = "\n\n💡 *Hotstar layout may have changed. Try again later.*"
        else:
            hint = ""
        try:
            await status_msg.edit_text(f"💥 **Error:** `{err[:150]}`{hint}", parse_mode="Markdown")
        except Exception:
            try:
                await update.message.reply_text(f"💥 **Error:** `{err[:150]}`{hint}", parse_mode="Markdown")
            except Exception:
                pass
        return ConversationHandler.END


async def receive_otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    user = update.effective_user
    otp = update.message.text.strip()

    if not otp.isdigit() or len(otp) != 4:
        await update.message.reply_text("⚠️ **Enter the 4-digit OTP.**", parse_mode="Markdown")
        return GET_OTP

    if chat_id not in user_sessions:
        await update.message.reply_text("⏰ **Session expired.** /start again.")
        return ConversationHandler.END

    session = user_sessions[chat_id]
    page = session["page"]
    mobile = session["mobile"]
    success_event: asyncio.Event = session["success_event"]

    async def on_response(response):
        try:
            if "payment/status" in response.url:
                data = await response.json()
                s = str(data).lower()
                if "active on" in s or "congratulations" in s or "success" in s:
                    session["payment_success"] = True
                    success_event.set()
        except Exception:
            pass

    page.on("response", on_response)
    page.set_default_timeout(90000)
    page.set_default_navigation_timeout(90000)
    status = await update.message.reply_text("🔄 *Verifying OTP...*", parse_mode="Markdown")

    try:
        otp_filled = False
        for sel_tpl in ["input[data-testid='id-{i}']",
                        "input[data-testid='otp-input-{i}']",
                        "input[name='otp-{i}']"]:
            try:
                ok = True
                for i, digit in enumerate(otp[:4]):
                    box = page.locator(sel_tpl.format(i=i))
                    if await box.count() == 0:
                        ok = False
                        break
                    await box.click()
                    await box.fill(digit)
                if ok:
                    otp_filled = True
                    break
            except Exception:
                continue

        if not otp_filled:
            for sel in ["input[autocomplete='one-time-code']", "input[inputmode='numeric']"]:
                loc = page.locator(sel).first
                try:
                    if await loc.count() > 0:
                        await loc.click()
                        await loc.type(otp[:4], delay=80)
                        otp_filled = True
                        break
                except Exception:
                    continue

        continue_btn = page.locator(
            "button[data-testid='otp-form-submit-button'], "
            "button:has-text('Continue'), button:has-text('Verify'), button[type='submit']"
        ).first
        try:
            if await continue_btn.count() > 0:
                await continue_btn.click(timeout=15000)
        except Exception:
            pass

        await page.wait_for_timeout(4000)

        # Device limit
        try:
            if await page.locator("text=Log Out 2 Devices to Continue").count() > 0 or \
               await page.locator("text=Device Limit Reached").count() > 0:
                logout_btn = page.locator("button:has-text('Log Out 2 Devices'), button:has-text('Log Out')").first
                if await logout_btn.count() > 0:
                    await logout_btn.click(timeout=10000)
                    await page.wait_for_timeout(2500)
                    try:
                        if await continue_btn.count() > 0:
                            await continue_btn.click(timeout=10000)
                            await page.wait_for_timeout(2500)
                    except Exception:
                        pass
        except Exception:
            pass

        # Ineligible
        if await page.locator("text=User not eligible for this plan").count() > 0:
            u = get_user(user)
            update_user(user.id, total_not_valid=u.get("total_not_valid", 0) + 1)
            await status.edit_text(
                "❌ **User Ineligible for this Plan!**\n\n"
                f"📱 `+91 {mobile}` already has an active plan.\n\n"
                "💡 *No point deducted.*",
                parse_mode="Markdown"
            )
            await safe_close_session(chat_id)
            return ConversationHandler.END

        # Already subscribed
        if await page.locator("text=You're already subscribed to this plan").count() > 0:
            u = get_user(user)
            update_user(user.id, total_not_valid=u.get("total_not_valid", 0) + 1)
            await status.edit_text(
                "⭐ **Already Subscribed!**\n\n"
                f"📱 `+91 {mobile}` already on this plan.\n\n"
                "💡 *No point deducted.*",
                parse_mode="Markdown"
            )
            await safe_close_session(chat_id)
            return ConversationHandler.END

        # Incorrect OTP
        if await page.locator("text=Incorrect OTP entered. Please enter again.").count() > 0:
            u = get_user(user)
            update_user(user.id, total_incorrect_otp=u.get("total_incorrect_otp", 0) + 1)
            await status.edit_text(
                "❌ **Incorrect OTP!** /start to try again.\n\n"
                "💡 *No point deducted.*",
                parse_mode="Markdown"
            )
            await safe_close_session(chat_id)
            return ConversationHandler.END

        # Redirect back to offer
        await status.edit_text("🔄 *Redirecting to ₹1 Offer Checkout...*", parse_mode="Markdown")
        try:
            await page.goto(HOTSTAR_PREMIUM_URL, timeout=90000, wait_until="commit")
        except Exception:
            pass
        await page.wait_for_timeout(4000)

        if await page.locator("text=User not eligible for this plan").count() > 0 or \
           await page.locator("text=You're already subscribed to this plan").count() > 0:
            u = get_user(user)
            update_user(user.id, total_not_valid=u.get("total_not_valid", 0) + 1)
            await status.edit_text(
                "❌ **Plan Not Applicable!**\n\n"
                "💡 *No point deducted.*",
                parse_mode="Markdown"
            )
            await safe_close_session(chat_id)
            return ConversationHandler.END

        # QR
        try:
            qr_btn = page.locator("button:has-text('Show QR Code')")
            await qr_btn.click(timeout=8000)
            await page.wait_for_timeout(2000)
        except Exception:
            pass

        qr_path = Path.cwd() / f"qr_{chat_id}.png"
        await page.screenshot(path=str(qr_path), full_page=True)
        try:
            await status.delete()
        except Exception:
            pass

        with open(qr_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=(
                    "📸 **Scan QR Code to Pay ₹1**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⏳ *Waiting for payment...*\n\n"
                    "💡 *1 point will be deducted on SUCCESS only.*"
                ),
                parse_mode="Markdown"
            )
        qr_path.unlink(missing_ok=True)

        tracking = await update.message.reply_text("⏳ *Tracking payment...*", parse_mode="Markdown")

        try:
            await asyncio.wait_for(success_event.wait(), timeout=150)
        except asyncio.TimeoutError:
            pass

        succ_path = Path.cwd() / f"succ_{chat_id}.png"
        try:
            await page.screenshot(path=str(succ_path), full_page=True)
        except Exception:
            pass
        try:
            await tracking.delete()
        except Exception:
            pass

        # ---------- SUCCESS: DEDUCT POINT HERE ----------
        if session["payment_success"]:
            u = get_user(user)
            # Only deduct if not already charged AND user is NOT admin
            if not session.get("charged") and not is_admin(user.id):
                new_bal = max(0, u.get("balance", 0) - 1)
                update_user(user.id,
                            balance=new_bal,
                            total_success=u.get("total_success", 0) + 1)
                session["charged"] = True
                remaining = str(new_bal)
            else:
                # Admin — count success but no deduction
                update_user(user.id, total_success=u.get("total_success", 0) + 1)
                session["charged"] = True
                remaining = "∞ (Owner)" if is_admin(user.id) else str(u.get("balance", 0))

            caption = (
                "🎉 **Payment Successful!**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 `+91 {mobile}`\n"
                "✅ Premium 1 Month Activated\n\n"
                f"💳 **Remaining Balance:** `{remaining}`\n"
                f"➖ **Deducted:** `1` point"
            )
            if is_admin(user.id):
                caption = (
                    "🎉 **Payment Successful!**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📱 `+91 {mobile}`\n"
                    "✅ Premium 1 Month Activated\n\n"
                    "👑 **Owner — no points deducted.**"
                )
        else:
            u = get_user(user)
            update_user(user.id, total_payment_stuck=u.get("total_payment_stuck", 0) + 1)
            caption = (
                "⏳ **Payment Status Unknown / Stuck**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 `+91 {mobile}`\n"
                "Check screenshot for final status.\n\n"
                "💡 *No point deducted.*"
            )

        try:
            with open(succ_path, "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=caption, parse_mode="Markdown")
            succ_path.unlink(missing_ok=True)
        except Exception:
            await update.message.reply_text(caption, parse_mode="Markdown")

        await safe_close_session(chat_id)

    except Exception as e:
        logger.error(f"receive_otp error: {e}")
        u = get_user(user)
        update_user(user.id, total_payment_stuck=u.get("total_payment_stuck", 0) + 1)
        try:
            await update.message.reply_text(
                f"❌ **Error:** `{str(e)[:200]}`\n\n💡 *No point deducted.*",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await safe_close_session(chat_id)
        return ConversationHandler.END

    return ConversationHandler.END


async def cancel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    await safe_close_session(chat_id)
    if update.callback_query:
        try:
            await update.callback_query.answer()
        except Exception:
            pass
        try:
            await update.callback_query.message.edit_text(
                "🛑 **Cancelled.** Use /start to begin again.\n\n"
                "💡 *No point deducted.*",
                reply_markup=back_kb(), parse_mode="Markdown"
            )
        except Exception:
            pass
    else:
        await update.message.reply_text(
            "🛑 **Cancelled.** /start to begin again.",
            parse_mode="Markdown"
        )
    return ConversationHandler.END


# ---------------- GENERIC CALLBACK ----------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    data = query.data

    if data == "menu_home":
        await show_main_menu(update, context, edit=True)
    elif data == "menu_info":
        await info_command(update, context)
    elif data == "menu_help":
        await help_command(update, context)
    elif data == "menu_balance":
        await balance_command(update, context)
    elif data == "menu_redeem":
        try:
            await query.message.edit_text(
                "🔑 **Redeem Your Key**\n\n"
                "Send: `/code YOURKEY`\n"
                "Example: `/code ABC123XYZ`",
                reply_markup=back_kb(), parse_mode="Markdown"
            )
        except Exception:
            pass
    elif data == "menu_admin":
        if not is_admin(update.effective_user.id):
            return
        try:
            await query.message.edit_text(
                "🛠 **Admin Panel**\n\n"
                "👑 *Owner mode active — unlimited balance.*",
                reply_markup=admin_panel_kb(), parse_mode="Markdown"
            )
        except Exception:
            pass
    elif data == "admin_stats":
        await stats_command(update, context)
    elif data == "admin_users":
        if not is_admin(update.effective_user.id):
            return
        users = load_users()
        lines = [f"`{uid}` | 💳{u.get('balance', 0)} | ✅{u.get('total_success', 0)}"
                 for uid, u in list(users.items())[:30]]
        text = f"👥 **Total Users:** `{len(users)}`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + ("\n".join(lines) if lines else "None")
        try:
            await query.message.edit_text(text, reply_markup=back_kb("menu_admin"), parse_mode="Markdown")
        except Exception:
            pass
    elif data == "admin_keyhelp":
        if not is_admin(update.effective_user.id):
            return
        try:
            await query.message.edit_text(
                "🔑 **Key Generation**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`/gen <count> <uses> <days>`\n\n"
                "**Example:**\n"
                "`/gen 5 6 1` → 5 keys × 6 uses × 1 day\n"
                "`/gen 1 6 1` → 1 key × 6 uses × 1 day\n\n"
                "Each key can be redeemed once via `/code KEY`.",
                reply_markup=back_kb("menu_admin"), parse_mode="Markdown"
            )
        except Exception:
            pass
    elif data == "cancel_flow":
        await cancel_flow(update, context)


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_flow_cb, pattern="^menu_start$"),
        ],
        states={
            GET_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_number),
                CallbackQueryHandler(cancel_flow, pattern="^cancel_flow$"),
            ],
            GET_OTP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_otp),
                CallbackQueryHandler(cancel_flow, pattern="^cancel_flow$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_flow),
            CallbackQueryHandler(cancel_flow, pattern="^cancel_flow$"),
        ],
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("code", code_command))
    app.add_handler(CommandHandler("cancel", cancel_flow))

    # Admin
    app.add_handler(CommandHandler("gen", gen_command))
    app.add_handler(CommandHandler("addbal", addbal_command))
    app.add_handler(CommandHandler("removebal", removebal_command))
    app.add_handler(CommandHandler("resetbal", resetbal_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("user", user_command))
    app.add_handler(CommandHandler("allusers", allusers_command))
    app.add_handler(CommandHandler("keys", keys_command))

    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Hotstar Bot running — v3 (owner unlimited + success-only deduction)")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
