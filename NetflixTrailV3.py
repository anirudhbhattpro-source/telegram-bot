import telebot
from telebot.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import requests
import os
import re
import uuid
import time
import random
import sys
import threading
import html
import signal
import base64
import quopri
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================
# 🤖 TELEGRAM BOT CONFIGURATION
# ============================================
TOKEN = "8984518700:AAGhj4Fsp3556f-A8gRqGaZQrcf1Tr0jPr0"
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

OUTPUT_FOLDER = ".cache"
LOGS_FOLDER = "logs"

for folder in [OUTPUT_FOLDER, LOGS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# ============================================
# 👤 OWNER CONFIGURATION
# ============================================
OWNER_USERNAME = "Baadsahhabhai"
OWNER_ID = 5390129810
OWNER_CONTACT = "@Baadsahhabhai"

# ============================================
# 🌟 PREMIUM EMOJI IDs - COMPLETE FIXED
# ============================================
PREMIUM_EMOJI_IDS = {
    # ===== YOUR CUSTOM EMOJIS =====
    "📚": "5222444124698853913",
    "🎬": "6293821461828211185",
    "📱": "6294135870614147548",
    "🎵": "5271527792641595125",
    
    # ===== NUMBER EMOJIS =====
    "1️⃣": "5235776368905562305",
    "2️⃣": "5237704680372447424",
    "3️⃣": "5238044171767393675",
    "4️⃣": "5235533321001250232",
    "5️⃣": "5238171599152097811",
    "6️⃣": "5235500881113263583",
    "7️⃣": "5237875542761417785",
    "8️⃣": "5238067300166281132",
    "9️⃣": "5237872922831367023",
    
    # ===== SUCCESS / ERROR =====
    "✅": "5974482805055296929",
    "❌": "5447647474984449520",
    "✔️": "6269285159774720688",
    "✖️": "6269362834258269327",
    "☑️": "6293939284774090470",
    "⛔": "6269391327071310756",
    "🚫": "5116151848855667552",
    "🚷": "6269019133795374514",

    # ===== FIRE / ENERGY =====
    "🔥": "5463094762951156490",
    "⚡": "5219943216781995020",
    "💥": "5122933683820430249",
    "✨": "6111706443226811437",
    "🌟": "5310224206732996002",
    "⭐": "6267298050205553492",
    "⭐️": "5172716095697584957",

    # ===== PAYMENT / MONEY =====
    "💳": "5447453226498552490",
    "💰": "5116648080787112958",
    "💸": "5283232570660634549",
    "💵": "5350711759625795085",
    "🛒": "5447319442562251569",

    # ===== EMAIL / MESSAGES =====
    "📧": "5445174334031166029",
    "📝": "6266764202950530136",
    "📋": "5197269100878907942",
    "📄": "5447421246172069841",
    "📁": "5444908424015934570",
    "📂": "5444908424015934570",
    "📎": "5282531402821991529",
    "💬": "5447510826304959724",
    "📢": "5116445341150872576",
    "📣": "6294335475831402267",

    # ===== TIME / WAITING =====
    "⏳": "5258113901106580375",
    "⏱️": "5343927661213279013",
    "🕒": "5258113901106580375",
    "📅": "5343927661213279013",
    "📆": "5343927661213279013",

    # ===== BOT / TECH =====
    "🤖": "5931415565955503486",
    "💠": "5931415565955503486",
    "🖥️": "5258574977633567931",
    "⌨️": "5258334330740171131",
    "⚙️": "5258023599419171861",
    "🔧": "4904936030232117798",
    "🛠️": "5348239232852836489",
    "🔌": "5120722716260828125",
    "📡": "5447448489149625830",
    "📱": "6294135870614147548",

    # ===== ARROWS / NAVIGATION =====
    "➡️": "5445350109862720603",
    "⬆️": "6294333051171504462",
    "🆙": "6294340079310882490",
    "🔝": "6294480298292978540",
    "👇": "5122933683820430249",
    "🔘": "5219901967916084166",
    "🔗": "5447479640547428304",

    # ===== SECURITY =====
    "🔐": "5258476306152038031",
    "🔒": "5258476306152038031",
    "🔓": "5258476306152038031",
    "🛡": "5219672809936006424",
    "🛡️": "5219672809936006424",

    # ===== PEOPLE =====
    "👋": "5134476056241112076",
    "👤": "5445174334031166029",
    "👥": "5454371323595744068",
    "🤝": "6294277024714330420",
    "👍": "6293942330341191383",
    "👌": "5445350109862720603",
    "😇": "6321225560789877992",
    "😈": "6294689498544548570",
    "👼": "6294692930487654291",
    "😉": "6294725541421455150",
    "😪": "6294365553102224020",
    "🥰": "5444931419270839381",
    "😱": "5447181973544008180",
    "😺": "5118590136149345664",

    # ===== HEARTS / FEELINGS =====
    "❤️": "5352918496642604333",
    "💔": "6078087767106001151",
    "💜": "6294147639899098147",
    "💟": "6294716179705691554",
    "🩸": "5352727529511723136",
    "🤍": "6293870742282965014",

    # ===== ANIMALS / NATURE =====
    "🦁": "6294261187671614577",
    "🦉": "5123344136665039833",
    "🌍": "5303440357428586778",
    "🌐": "5447602197439218445",
    "🌝": "5341684837881235158",

    # ===== FOOD =====
    "🍑": "5445408306669582934",
    "🍭": "6267152480878990865",
    "🍳": "5305622454218024328",
    "🥕": "5447653032672129347",

    # ===== OBJECTS =====
    "👑": "6266995104687330978",
    "💎": "5343636681473935403",
    "🎁": "5283031441637148958",
    "🎩": "6294592576045001736",
    "🎉": "5172632227871196306",
    "📦": "5303102515301083665",
    "📹": "5445158077579952110",
    "📼": "6294520683936559961",
    "📓": "6294487094370784696",
    "💭": "6294488407133457486",
    "🔫": "6294206328010435087",
    "⚔️": "6294135887794019865",
    "💼": "6294080753298837622",

    # ===== COLORS =====
    "🟢": "5269745613092546526",
    "🔴": "5269755666246672966",
    "🟡": "5269763542291111780",
    "🟣": "5269756223455927435",
    "🔵": "5269765444863100855",
    "⚪": "5269764171217530926",
    "🟨": "6294732630698888962",
    "🔷": "5301275719681190738",
    "🔹": "5301275719681190738",

    # ===== MISC =====
    "🚀": "5343887395894882351",
    "⚠️": "4915853119839011973",
    "💡": "5301275719681190738",
    "📈": "5134457377428341766",
    "📊": "5445146408153806223",
    "🔢": "5444931419270839381",
    "🆓": "5406756500108501710",
    "🆔": "5447311106030726740",
    "🆕": "5447311106030726740",
    "🎯": "5447187153274567373",
    "🔍": "5258396243666681152",
    "🔑": "5454386656628991407",
    "🏦": "5445408306669582934",
    "🔄": "5454245266305604993",
    "⛔️": "5275969776668134187",
    "🥲": "4904468402782864209",
    "☠️": "5231338559587257737",
    "💀": "5231338559587257737",
    "💪": "5305622454218024328",
    "ℹ️": "5289930378885214069",
    "📥": "5350747347724810871",
    "📤": "5350747347724810871",
    "️🏷️": "5436285465420383204",
    "📄️": "5323538339062628165",
    "🕒": "5258113901106580375",
    "✖": "6269355257935958587",
    "🔊": "6294714147760055534",
    
    # ===== OWNER CONTACT =====
    "👨‍💻": "5445174334031166029",
    "📞": "5447453226498552490",
    "💌": "5447510826304959724",
    "🏠": "5303102515301083665",
    "📬": "5447510826304959724",
    "📨": "5447510826304959724",
    "📩": "5447510826304959724",
}

def premium_emoji(text: str) -> str:
    if not text:
        return text
    result = text
    for emoji, emoji_id in PREMIUM_EMOJI_IDS.items():
        if emoji in result:
            if emoji_id and isinstance(emoji_id, str) and emoji_id.strip():
                try:
                    result = result.replace(emoji, f'<tg-emoji emoji-id="{emoji_id}">{emoji}</tg-emoji>')
                except Exception:
                    pass
    return result

# ============================================
# 🎨 UI FUNCTIONS - FIXED
# ============================================
def create_main_menu():
    """Create main menu keyboard with premium emojis"""
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = KeyboardButton("🎬 30 Days Trial")
    btn2 = KeyboardButton("⚡ 7 Days Trial")
    btn3 = KeyboardButton("✏️ Custom Email")
    btn4 = KeyboardButton("📊 Bulk Generate")
    btn5 = KeyboardButton("ℹ️ Help")
    btn6 = KeyboardButton("👨‍💻 Owner")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

def create_email_type_buttons(days):
    """Create email type selection buttons"""
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("🔄 Auto Email", callback_data=f"auto_{days}")
    btn2 = InlineKeyboardButton("✏️ Custom Email", callback_data=f"custom_{days}")
    btn3 = InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

def create_bulk_buttons():
    """Create bulk selection buttons with number emojis"""
    markup = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 6):
        # Use number emojis
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][i-1]
        btn = InlineKeyboardButton(f"{emoji}", callback_data=f"bulk_{i}")
        buttons.append(btn)
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    return markup

# ============================================
# 🍪 COOKIES
# ============================================
COOKIE_30_DAYS = """# Netflix Account - 30 Days Trial (Updated)
.netflix.com	TRUE	/	FALSE	1794057632	netflix-sans-normal-3-loaded	true
.netflix.com	TRUE	/	TRUE	1817817625	SecureNetflixId	v%3D3%26mac%3DAQEAEQABABSDOrFMrAWpV18Q2Xw9jGwajzzd6M_fXto.%26dt%3D1786281625612
.netflix.com	TRUE	/	FALSE	1786202603	firstLolomoAfterOnRamp	true
www.netflix.com	FALSE	/	FALSE	1786368037	OTSessionTracking	87b6a5c0-0104-4e96-a291-092c11350111
#HttpOnly_.netflix.com	TRUE	/	TRUE	1786293437	gsid	9e270386-6cfe-401b-b833-7e6dbc496f34
.netflix.com	TRUE	/	FALSE	1817817625	NetflixId	v%3D3%26ct%3DBgjHlOvcAxLAAT3tcqcUO4x8RGnAlWde2qcyhaa1sydi7k0UYJDXDPNo85tZXlfjzEdeqLMpAx4sJk7eLmWdKyFVK_FSuuKRcNKTX1Snt0cYTXQWVltdWf8FPFcaUxnMpcjhVNteYH-AzCE1VySpiBk_VbmveT-1dFUiuCK7I1hbZlX3nTRdFabizVsCnhSjJv7QNZOvrxDauYv0DRKKGvA2C1xiQruG1Y7xifa6RIIpBEFKifYjzCTaHjlLICYon3D0tI38w2B2xhgGIg4KDOtj99wIy2Tzvxwmzw..
.netflix.com	TRUE	/	FALSE	1817817637	OptanonConsent	isGpcEnabled=0&datestamp=Sun+Aug+09+2026+18%3A50%3A37+GMT%2B0530+(India+Standard+Time)&version=202604.2.0&browserGpcFlag=0&isDntEnabled=0&isIABGlobal=false&hosts=&consentId=c1e82145-2cf8-45e3-a994-05c86658a570&interactionCount=0&isAnonUser=1&prevHadToken=0&landingPath=https%3A%2F%2Fwww.netflix.com%2Fin%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1
.netflix.com	TRUE	/	FALSE	1786292432	flwssn	d1215a03-1faa-4322-8f3c-5bb2ef7fe691
.netflix.com	TRUE	/	FALSE	1794057632	netflix-sans-bold-3-loaded	true
.netflix.com	TRUE	/	FALSE	1817743037	nfvdid	BQFmAAEBEP0rTz8aNXNFtQ4_y1_ZsrpAsLUMjbvcMjcz5KIOKkOaKvESl76OKOfDR6wgeLHHzYkFbSXaadhW2oqQTNC9Rp7IpqlDff2Ut-bXgA7rnJPBew%3D%3D"""

COOKIE_7_DAYS = """# Netflix Account - 7 Days Trial
.netflix.com	TRUE	/	FALSE	1793982954	netflix-sans-normal-3-loaded	true
.netflix.com	TRUE	/	TRUE	1817742953	SecureNetflixId	v%3D3%26mac%3DAQEAEQABABQ6HZRqIhRW0d13B4L_C6syWZx4_tuqqSQ.%26dt%3D1786206952985
.netflix.com	TRUE	/	FALSE	1786202603	firstLolomoAfterOnRamp	true
www.netflix.com	FALSE	/	FALSE	1786274001	OTSessionTracking	87b6a5c0-0104-4e96-a291-092c11350111
#HttpOnly_.netflix.com	TRUE	/	TRUE	1786293353	gsid	fd079b0e-3f88-409f-a0d7-51b3615b6f69
.netflix.com	TRUE	/	TRUE	1817742953	NetflixId	v%3D3%26ct%3DBgjHlOvcAxLAAXygryfDBR1KXSr8t2jTFm8BJzbdWHZdHKPwoB926rFNw2zTEJDuSNPl6ilBgOGEhFl8WChu4gyVAh-2bPP3BwgKpthHM192s14aweNc2duF3a2PdSFy-p8k9bXyo8QSjQBIZgyF3oyjr-HPJCJAloSJgxc9Wu2a9ea6o4i3i9bKzdWoQEfvccZu7hHMLPlWYv8UBq4cVpZ1whAi32JUf9LWNiJ7NiMWZVJJj9evxaH_HxB7pIFqQ8dPZu0nUdjj0hgGIg4KDIm5JG6_pIZhtehCww..
.netflix.com	TRUE	/	FALSE	1817742955	OptanonConsent	isGpcEnabled=0&datestamp=Sat+Aug+08+2026+22%3A05%3A55+GMT%2B0530+(India+Standard+Time)&version=202604.2.0&browserGpcFlag=0&isDntEnabled=0&isIABGlobal=false&hosts=&consentId=1003978a-f764-4660-8a59-9a03df527871&interactionCount=0&isAnonUser=1&prevHadToken=0&landingPath=https%3A%2F%2Fwww.netflix.com%2Fin%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1
.netflix.com	TRUE	/	FALSE	1786217753	flwssn	3d5e111f-f9f6-4042-82d7-6c233d4824f4
.netflix.com	TRUE	/	FALSE	1793982954	netflix-sans-bold-3-loaded	true
.netflix.com	TRUE	/	FALSE	1817742953	nfvdid	BQFmAAEBEDgky-_o1VmGOGdWq4jYC1NAiEJ5exU-mZkIQINL0YsgB0WeenDdN_jgL-y49IYGtKB3_cj9ZJMaG7Jxl58-cVX1sYHHtIF_TXdjJGIHRIHpEg%3D%3D"""

COOKIES = {"30": COOKIE_30_DAYS, "7": COOKIE_7_DAYS}

def parse_netscape_cookie(cookie_text):
    cookies = {}
    for line in cookie_text.strip().split('\n'):
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        parts = line.split('\t')
        if len(parts) >= 7:
            name = parts[5]
            value = parts[6]
            if name in ['NetflixId', 'SecureNetflixId', 'flwssn', 'gsid', 'nfvdid']:
                cookies[name] = value
    return cookies

def parse_cookie_content(content):
    cookies = parse_netscape_cookie(content)
    if cookies and ('NetflixId' in cookies or 'SecureNetflixId' in cookies):
        return cookies, "Netscape"
    return None, None

def build_cookie_string(cookies):
    cookie_parts = []
    for name, value in cookies.items():
        cookie_parts.append(f"{name}={value}")
    return "; ".join(cookie_parts)

# ============================================
# 🛠 UTILITY FUNCTIONS
# ============================================
def extract_flwssn(cookie_string):
    match = re.search(r'flwssn=([^;]+)', cookie_string)
    if match:
        return match.group(1)
    return str(uuid.uuid4())

def extract_gsid(cookie_string):
    match = re.search(r'gsid=([^;]+)', cookie_string)
    if match:
        return match.group(1)
    return str(uuid.uuid4())

def generate_request_id():
    return uuid.uuid4().hex[:32]

def generate_toplevel_uuid():
    return str(uuid.uuid4())

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(user_agents)

# ============================================
# 📧 EMAIL DECODING FUNCTIONS
# ============================================
def decode_email_content(encoded_text):
    if not encoded_text:
        return ""
    try:
        decoded = base64.b64decode(encoded_text).decode('utf-8', errors='ignore')
        return decoded
    except:
        try:
            decoded = quopri.decodestring(encoded_text.encode()).decode('utf-8', errors='ignore')
            return decoded
        except:
            return encoded_text

def clean_html_to_text(html_content):
    if not html_content:
        return "No content"
    if isinstance(html_content, list):
        html_content = ' '.join(str(item) for item in html_content)
    
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</p>', '\n\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</div>', '\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<li>', '• ', html_content, flags=re.IGNORECASE)
    
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text if text else "No readable content"

def extract_all_links(html_content):
    if not html_content:
        return []
    links = []
    href_pattern = r'href=["\'](https?://[^"\']+)["\']'
    matches = re.findall(href_pattern, html_content, re.IGNORECASE)
    links.extend(matches)
    url_pattern = r'https?://[^\s"\'<>]+'
    matches = re.findall(url_pattern, html_content, re.IGNORECASE)
    links.extend(matches)
    unique_links = []
    for link in links:
        if link and 'http' in link:
            link = re.sub(r'[.,;:!?]+$', '', link)
            if link not in unique_links:
                unique_links.append(link)
    return unique_links

def extract_epr_link(html_content):
    if not html_content:
        return None
    patterns = [
        r'https?://[^\s"\'<>]*netflix\.com/epr\?code=[^\s"\'<>]+',
        r'https?://[^\s"\'<>]*netflix\.com/epr[^\s"\'<>]*',
        r'https?://[^\s"\'<>]*netflix\.com[^\s"\'<>]*(?:signup|create|start|join|trial|account)[^\s"\'<>]*',
        r'href=["\']([^"\']*netflix\.com[^"\']*(?:epr|signup|create|start)[^"\']*)["\']',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ''
            if match and 'http' in match:
                match = re.sub(r'[.,;:!?]+$', '', match)
                return match
    return None

def extract_checkout_link(html_content):
    if not html_content:
        return None
    patterns = [
        r'https?://[^\s"\'<>]*netflix\.com[^\s"\'<>]*(?:checkout|payment|pay|confirm|order)[^\s"\'<>]*',
        r'href=["\']([^"\']*netflix\.com[^"\']*(?:checkout|payment|pay|confirm|order)[^"\']*)["\']',
        r'https?://[^\s"\'<>]*netflix\.com[^\s"\'<>]*/payment/[^\s"\'<>]*',
        r'https?://[^\s"\'<>]*netflix\.com[^\s"\'<>]*(?:plan|choose|select|premium|standard|basic)[^\s"\'<>]*',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ''
            if match and 'http' in match:
                match = re.sub(r'[.,;:!?]+$', '', match)
                return match
    return None

# ============================================
# 📧 MAIL.TM CLASS
# ============================================
class MailTM:
    def __init__(self):
        self.token = None
        self.email = None
        self.password = None
        self.account_id = None
        self.web_url = None
        self.api_url = "https://api.mail.tm"
    
    def create_account(self):
        try:
            resp = requests.get(f"{self.api_url}/domains")
            if resp.status_code != 200:
                return False, "Failed to get domains"
            
            domains = resp.json()
            if not domains or 'hydra:member' not in domains:
                return False, "No domains available"
            
            domain = domains['hydra:member'][0]['domain']
            
            username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
            self.email = f"{username}@{domain}"
            self.password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
            
            account_data = {"address": self.email, "password": self.password}
            resp = requests.post(f"{self.api_url}/accounts", json=account_data)
            if resp.status_code != 201:
                return False, f"Account creation failed"
            
            account = resp.json()
            self.account_id = account['id']
            self.web_url = f"https://mail.tm/#/inbox/{account['id']}"
            
            token_data = {"address": self.email, "password": self.password}
            resp = requests.post(f"{self.api_url}/token", json=token_data)
            if resp.status_code != 200:
                return False, "Token generation failed"
            
            self.token = resp.json()['token']
            
            return True, {
                'email': self.email,
                'password': self.password,
                'web_inbox': self.web_url,
                'account_id': self.account_id
            }
            
        except Exception as e:
            return False, str(e)
    
    def get_messages(self):
        if not self.token:
            return []
        headers = {"Authorization"
