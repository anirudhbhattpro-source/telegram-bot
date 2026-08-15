# NetflixTrailV3_PC.py - Complete Updated Version with PC Fixes

# ============================================
# 🖥️ PC FIXES - MUST BE AT TOP
# ============================================
import sys
import os
import ssl
import warnings
import certifi

# Disable SSL Warnings
warnings.filterwarnings('ignore')

# Fix SSL for Windows
try:
    import certifi
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except:
    pass

# Fix Encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import after fixes
import telebot
from telebot.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import requests
import re
import uuid
import time
import random
import threading
import html
import signal
import base64
import quopri
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL verification globally (fix for PC)
requests.packages.urllib3.disable_warnings()

# ============================================
# 🤖 TELEGRAM BOT CONFIGURATION
# ============================================
TOKEN = "8984518700:AAHWP9QclT9QDwwTPBYBJ_l3qww7i3CyXrI"
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
# 🎨 UI FUNCTIONS
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
# 📧 MAIL.TM CLASS - WITH PC FIXES
# ============================================
class MailTM:
    def __init__(self):
        self.token = None
        self.email = None
        self.password = None
        self.account_id = None
        self.web_url = None
        self.api_url = "https://api.mail.tm"
        self.session = self._create_session()
    
    def _create_session(self):
        """Create a session with SSL fixes for PC"""
        session = requests.Session()
        try:
            # Try to use certifi for SSL
            import certifi
            session.verify = certifi.where()
        except:
            # Fallback: disable SSL verification
            session.verify = False
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        return session
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make request with error handling"""
        url = f"{self.api_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.SSLError:
            # If SSL error, retry with verification disabled
            self.session.verify = False
            return self.session.request(method, url, timeout=30, **kwargs)
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def create_account(self):
        try:
            resp = self._make_request('GET', '/domains')
            if not resp or resp.status_code != 200:
                return False, "Failed to get domains"
            
            domains = resp.json()
            if not domains or 'hydra:member' not in domains or not domains['hydra:member']:
                return False, "No domains available"
            
            domain = domains['hydra:member'][0]['domain']
            
            username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
            self.email = f"{username}@{domain}"
            self.password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
            
            account_data = {"address": self.email, "password": self.password}
            resp = self._make_request('POST', '/accounts', json=account_data)
            if not resp or resp.status_code != 201:
                return False, f"Account creation failed: {resp.status_code if resp else 'No response'}"
            
            account = resp.json()
            self.account_id = account['id']
            self.web_url = f"https://mail.tm/#/inbox/{account['id']}"
            
            token_data = {"address": self.email, "password": self.password}
            resp = self._make_request('POST', '/token', json=token_data)
            if not resp or resp.status_code != 200:
                return False, "Token generation failed"
            
            self.token = resp.json()['token']
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            
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
        try:
            resp = self._make_request('GET', '/messages')
            if resp and resp.status_code == 200:
                data = resp.json()
                return data.get('hydra:member', [])
        except:
            pass
        return []
    
    def get_message_content(self, message_id):
        if not self.token:
            return None
        try:
            resp = self._make_request('GET', f'/messages/{message_id}')
            if resp and resp.status_code == 200:
                return resp.json()
        except:
            pass
        return None
    
    def wait_for_email(self, timeout=90, check_interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = self.get_messages()
            if messages:
                latest = messages[0]
                content = self.get_message_content(latest['id'])
                if content:
                    html_content = content.get('html', [''])[0] if isinstance(content.get('html'), list) else content.get('html', '')
                    text_content = content.get('text', [''])[0] if isinstance(content.get('text'), list) else content.get('text', '')
                    
                    if html_content and html_content.startswith('='):
                        html_content = decode_email_content(html_content)
                    if text_content and text_content.startswith('='):
                        text_content = decode_email_content(text_content)
                    
                    content['html_decoded'] = html_content
                    content['text_decoded'] = text_content
                    content['web_link'] = f"https://mail.tm/#/inbox/{self.account_id}/{latest['id']}"
                    return content
            time.sleep(check_interval)
        return None

# ============================================
# 🚀 NETFLIX TRIAL SENDER - WITH PC FIXES
# ============================================
def send_trial_offer(email, cookie_string, retry_count=2):
    flwssn = extract_flwssn(cookie_string)
    gsid = extract_gsid(cookie_string)
    user_agent = get_random_user_agent()
    
    # Create session with SSL fixes
    session = requests.Session()
    try:
        import certifi
        session.verify = certifi.where()
    except:
        session.verify = False
    
    base_headers = {
        'authority': 'web.prod.cloud.netflix.com',
        'accept': '*/*',
        'accept-language': 'en-MM,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.netflix.com',
        'referer': 'https://www.netflix.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': user_agent
    }
    
    results = {}
    
    for attempt in range(retry_count + 1):
        try:
            headers = base_headers.copy()
            headers.update({
                'content-type': 'application/json',
                'cookie': cookie_string,
                'x-netflix.context.app-version': 'v38c5b0da',
                'x-netflix.context.form-factor': 'phone',
                'x-netflix.context.is-inapp-browser': 'false',
                'x-netflix.context.locales': 'en-in',
                'x-netflix.context.operation-name': 'CLCSWebInitSignup',
                'x-netflix.context.ui-flavor': 'akira',
                'x-netflix.request.attempt': str(attempt + 1),
                'x-netflix.request.clcs.bucket': 'high',
                'x-netflix.request.client.context': '{"appstate":"foreground"}',
                'x-netflix.request.id': generate_request_id(),
                'x-netflix.request.originating.url': 'https://www.netflix.com/in/',
                'x-netflix.request.toplevel.uuid': generate_toplevel_uuid()
            })
            
            data = {
                "operationName": "CLCSWebInitSignup",
                "variables": {
                    "inputNode": "WELCOME",
                    "locale": "en-IN",
                    "inputFields": [
                        {"name": "flwssn", "value": {"stringValue": flwssn}},
                        {"name": "email", "value": {"stringValue": email}},
                        {"name": "recaptchaError", "value": {"stringValue": "LOAD_TIMED_OUT"}},
                        {"name": "recaptchaResponseTime", "value": {}},
                        {"name": "recaptchaSiteKey", "value": {"stringValue": "6LdqW_EqAAAAAO87Fb_kcZfNzs0IqJRcKiJDYpUv"}},
                        {"name": "recaptchaToken", "value": {}}
                    ]
                },
                "extensions": {
                    "persistedQuery": {
                        "id": "5d76d6a0-ccfe-4c31-b587-b4e1954732ca",
                        "version": 102
                    }
                }
            }
            
            response = session.post('https://web.prod.cloud.netflix.com/graphql', 
                                    headers=headers, json=data, timeout=15)
            results['init'] = {'status': response.status_code}
            
            if response.status_code != 200:
                if attempt < retry_count:
                    time.sleep(random.uniform(1, 3))
                    continue
                return results, False
            
            headers = base_headers.copy()
            headers.update({
                'content-type': 'application/json',
                'cookie': cookie_string,
                'x-netflix.context.app-version': 'v38c5b0da',
                'x-netflix.context.form-factor': 'phone',
                'x-netflix.context.is-inapp-browser': 'false',
                'x-netflix.context.locales': 'en-in',
                'x-netflix.context.operation-name': 'CLCSScreenUpdate',
                'x-netflix.context.ui-flavor': 'akira',
                'x-netflix.request.attempt': str(attempt + 1),
                'x-netflix.request.clcs.bucket': 'high',
                'x-netflix.request.client.context': '{"appstate":"foreground"}',
                'x-netflix.request.id': generate_request_id(),
                'x-netflix.request.originating.url': 'https://www.netflix.com/signup',
                'x-netflix.request.toplevel.uuid': generate_toplevel_uuid()
            })
            
            data = {
                "operationName": "CLCSScreenUpdate",
                "variables": {
                    "format": "HTML",
                    "imageFormat": "PNG",
                    "locale": "en-IN",
                    "serverState": "Bgjru+vcAxLTAf/qOOEwXPLVxW+7Jod9WpjYuKN8j1qfhQpzCK4mmQts5eMSeaP+l7s6NKcNBO4rmYabFFCVnMpCH3ib4AicvXAKm30Z+s5W3Cst0D0BK5x/pwn3QmByi/OgGwU/fzaiR5oxSlZe4fKVexWHISkE4GMzJqLaaXQR0M73ynZB9idNBfqsz3RA5WJN+DGAbVUOZlWl8eZqffvQpp/5MGubeQFpdwKqkAx1nHh7/xI1i9tDU0KLgrvkZrbe6nQ1MX2nc9TBxqnVVxtc3ptHdqydP1wlIu0YBiIOCgydgLg1SvK6tSPOff8=",
                    "serverScreenUpdate": "Bgjru+vcAxKSAjDnHOxlaIbFSbwaWzZo/REHFnNG7OtpcXdKTDlcL4/o+huGi/fNW+jrqNDqDSsv1iytiG/ZtvO9ierUE9M1Kc/yEj9JsSiG3XpPciFDzPd6psSaG68XLbos+Qie0wniXCtJyWDLDuLd9ayCMB8qGCxwbov6B41kCQY/zArwlecm0GNoJdd5jvZfBJVtytD6mMCYnPA/9zhX4okj+6IGet9xOCYt76IDiuyESxgKbaOLcd6DQIDSBf4m/lYi2Tasj7olPkCaDIXxjU+0UY+b7eDyhvi2if2vt6510ARrGsSZq8DaazQmrpAbfiCW47s1/1mR59vUMYeT8VCqqAvbNwipqyP1DQMHtoTnCoWns0+x6IgYBiIOCgx9EW4i3i9SUswnHEg=",
                    "inputFields": [
                        {"name": "email", "value": {"stringValue": email}},
                        {"name": "pipcConsent", "value": {"booleanValue": False}}
                    ]
                },
                "extensions": {
                    "persistedQuery": {
                        "id": "0fd81de7-07af-4c7d-802f-0f4ea4181aa3",
                        "version": 102
                    }
                }
            }
            
            response = session.post('https://web.prod.cloud.netflix.com/graphql', 
                                    headers=headers, json=data, timeout=15)
            results['update'] = {'status': response.status_code}
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    html_content = resp_json.get('data', {}).get('screenUpdate', {}).get('html', '')
                    if html_content:
                        epr_link = extract_epr_link(html_content)
                        if epr_link:
                            results['epr_link'] = epr_link
                except:
                    pass
            
            return results, True
                
        except Exception as e:
            results['error'] = str(e)
            if attempt < retry_count:
                time.sleep(random.uniform(1, 3))
                continue
            return results, False
    
    return results, False

# ============================================
# 📧 PROCESS FUNCTIONS
# ============================================
def process_auto_email(chat_id, trial_type="30"):
    try:
        trial_days = "30" if trial_type == "30" else "7"
        trial_text = "30 Days" if trial_type == "30" else "7 Days"
        
        cookie_data = COOKIES.get(trial_type, COOKIES["30"])
        
        msg = f"""
{premium_emoji('🔥')} <b>Netflix Trial Generator</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📅')} <b>Trial:</b> {trial_text}
{premium_emoji('⏳')} <b>Status:</b> Creating temporary email...

⏱️ Please wait...
"""
        sent_msg = bot.send_message(chat_id, premium_emoji(msg), parse_mode='HTML')
        
        cookies, _ = parse_cookie_content(cookie_data)
        if not cookies:
            bot.edit_message_text(f"{premium_emoji('❌')} Invalid cookies!", chat_id, sent_msg.message_id)
            return
        
        cookie_string = build_cookie_string(cookies)
        
        mail = MailTM()
        success, result = mail.create_account()
        if not success:
            bot.edit_message_text(f"{premium_emoji('❌')} Failed: {result}", chat_id, sent_msg.message_id)
            return
        
        email = result['email']
        password = result['password']
        web_inbox = result['web_inbox']
        
        msg = f"""
{premium_emoji('✅')} <b>Email Created!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📧')} <b>Email:</b> <code>{email}</code>
{premium_emoji('🔑')} <b>Password:</b> <code>{password}</code>
{premium_emoji('📅')} <b>Trial:</b> {trial_text}
{premium_emoji('📬')} <b>Inbox:</b> <a href='{web_inbox}'>Click to Open</a>

{premium_emoji('🚀')} <b>Status:</b> Sending trial request...
"""
        bot.edit_message_text(premium_emoji(msg), chat_id, sent_msg.message_id, parse_mode='HTML')
        
        results, trial_success = send_trial_offer(email, cookie_string)
        if not trial_success:
            bot.send_message(chat_id, f"{premium_emoji('❌')} Trial failed for {email}")
            return
        
        bot.send_message(chat_id, f"{premium_emoji('⏳')} Waiting for Netflix email... (90 seconds)")
        
        email_content = mail.wait_for_email(timeout=90)
        
        if email_content:
            html_content = email_content.get('html_decoded', '')
            text_content = email_content.get('text_decoded', '')
            subject = email_content.get('subject', 'No Subject')
            email_link = email_content.get('web_link')
            
            epr_link = extract_epr_link(html_content)
            checkout_link = extract_checkout_link(html_content)
            all_links = extract_all_links(html_content)
            
            clean_text = clean_html_to_text(html_content)
            if len(clean_text) > 1500:
                clean_text = clean_text[:1500] + "..."
            
            msg = f"""
{premium_emoji('📨')} <b>Netflix Email Received!</b> {premium_emoji('✅')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📧')} <b>Email:</b> <code>{email}</code>
{premium_emoji('🔑')} <b>Password:</b> <code>{password}</code>
{premium_emoji('📅')} <b>Trial:</b> {trial_text}
{premium_emoji('📬')} <b>Inbox:</b> <a href='{web_inbox}'>Open Inbox</a>

{premium_emoji('📝')} <b>Subject:</b> {subject}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{premium_emoji('📄')} <b>Content:</b>

{clean_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            bot.send_message(chat_id, premium_emoji(msg), parse_mode='HTML')
            
            if epr_link:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f"{premium_emoji('🎬')} Create Account", url=epr_link))
                bot.send_message(chat_id, f"{premium_emoji('🔗')} Click below to create your Netflix account:", reply_markup=markup)
            
            if checkout_link:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f"{premium_emoji('💳')} Proceed to Payment", url=checkout_link))
                bot.send_message(chat_id, f"{premium_emoji('💳')} Checkout link:", reply_markup=markup)
            
            if email_link:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f"{premium_emoji('📬')} Open Email", url=email_link))
                bot.send_message(chat_id, f"{premium_emoji('📬')} Open email in browser:", reply_markup=markup)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{LOGS_FOLDER}/netflix_{trial_type}days_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'email': email,
                    'password': password,
                    'web_inbox': web_inbox,
                    'email_link': email_link,
                    'subject': subject,
                    'trial_type': trial_text,
                    'epr_link': epr_link,
                    'checkout_link': checkout_link,
                    'all_links': all_links,
                    'plain_text': clean_text
                }, f, indent=2, ensure_ascii=False)
            
            bot.send_message(chat_id, f"{premium_emoji('📁')} Saved to: {filename}")
            
        else:
            msg = f"""
{premium_emoji('⏳')} <b>No Email Received Yet</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📧')} <b>Email:</b> <code>{email}</code>
{premium_emoji('🔑')} <b>Password:</b> <code>{password}</code>
{premium_emoji('📬')} <b>Inbox:</b> <a href='{web_inbox}'>Open Inbox</a>

💡 Try refreshing inbox manually.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            bot.send_message(chat_id, premium_emoji(msg), parse_mode='HTML')
            
            if results.get('epr_link'):
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f"{premium_emoji('🔗')} Try Create Account", url=results['epr_link']))
                bot.send_message(chat_id, f"{premium_emoji('🔗')} Try this link:", reply_markup=markup)
    
    except Exception as e:
        bot.send_message(chat_id, f"{premium_emoji('❌')} Error: {str(e)}")

def process_custom_email(chat_id, email, days="7"):
    try:
        days_text = "7 Days" if days == "7" else "30 Days"
        msg = f"""
{premium_emoji('⏳')} <b>Processing {days_text}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📧')} <b>Email:</b> {email}

⏱️ Sending trial request...
"""
        bot.send_message(chat_id, premium_emoji(msg), parse_mode='HTML')
        
        cookie_string = build_cookie_string(parse_netscape_cookie(COOKIES.get(days, COOKIES["7"])))
        if not cookie_string:
            bot.send_message(chat_id, f"{premium_emoji('❌')} Invalid cookies!")
            return
        
        results, success = send_trial_offer(email, cookie_string)
        
        if success:
            msg = f"""
{premium_emoji('✅')} <b>Trial Sent!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📧')} <b>Email:</b> <code>{email}</code>
{premium_emoji('📅')} <b>Duration:</b> {days_text}

📌 <b>Next Steps:</b>
1️⃣ Check your inbox
2️⃣ Look for Netflix email
3️⃣ Click "Create Account"
4️⃣ Complete checkout

💡 Check SPAM folder if not in inbox
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{premium_emoji('👨‍💻')} <b>Owner:</b> {OWNER_CONTACT}
"""
            bot.send_message(chat_id, premium_emoji(msg), parse_mode='HTML')
            
            if results.get('epr_link'):
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f"{premium_emoji('🎬')} Create Account", url=results['epr_link']))
                bot.send_message(chat_id, f"{premium_emoji('🔗')} Create your Netflix account:", reply_markup=markup)
        else:
            bot.send_message(chat_id, f"{premium_emoji('❌')} Trial failed for {email}")
            
    except Exception as e:
        bot.send_message(chat_id, f"{premium_emoji('❌')} Error: {str(e)}")

def process_bulk_emails(chat_id, count):
    try:
        count = min(count, 5)
        msg = f"""
{premium_emoji('📊')} <b>Bulk Generation</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📦')} <b>Total:</b> {count}

{premium_emoji('⏳')} Generating...
"""
        sent_msg = bot.send_message(chat_id, premium_emoji(msg), parse_mode='HTML')
        
        cookie_string = build_cookie_string(parse_netscape_cookie(COOKIES["7"]))
        if not cookie_string:
            bot.edit_message_text(f"{premium_emoji('❌')} Invalid cookies!", chat_id, sent_msg.message_id)
            return
        
        results_list = []
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for _ in range(count):
                futures.append(executor.submit(process_one_bulk, cookie_string))
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=120)
                    results_list.append(result)
                    if result.get('success', False):
                        success_count += 1
                        email = result.get('email', 'Unknown')
                        bot.send_message(chat_id, f"{premium_emoji('✅')} {email}")
                except Exception as e:
                    bot.send_message(chat_id, f"{premium_emoji('❌')} Error: {str(e)[:50]}")
        
        summary = f"""
{premium_emoji('📊')} <b>Bulk Generation Complete!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📦')} <b>Total:</b> {len(results_list)}
{premium_emoji('✅')} <b>Success:</b> {success_count}
{premium_emoji('❌')} <b>Failed:</b> {len(results_list) - success_count}
{premium_emoji('📈')} <b>Rate:</b> {(success_count/len(results_list)*100 if results_list else 0):.1f}%

{premium_emoji('👨‍💻')} <b>Owner:</b> {OWNER_CONTACT}
"""
        bot.edit_message_text(premium_emoji(summary), chat_id, sent_msg.message_id, parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(chat_id, f"{premium_emoji('❌')} Error: {str(e)}")

def process_one_bulk(cookie_string):
    result = {'email': None, 'web_inbox': None, 'success': False}
    try:
        mail = MailTM()
        success, account = mail.create_account()
        if not success:
            return result
        
        email = account['email']
        web_inbox = account['web_inbox']
        
        result['email'] = email
        result['web_inbox'] = web_inbox
        
        results, trial_success = send_trial_offer(email, cookie_string)
        if trial_success:
            email_content = mail.wait_for_email(timeout=30)
            if email_content:
                result['success'] = True
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{LOGS_FOLDER}/bulk_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result

# ============================================
# 🤖 BOT COMMANDS
# ============================================
@bot.message_handler(commands=['start', 'menu'])
def start_command(message):
    chat_id = message.chat.id
    welcome = f"""
{premium_emoji('🎬')} <b>Netflix Trial Generator</b> {premium_emoji('🔥')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('🚀')} <b>Generate Free Netflix Trials</b>

{premium_emoji('📌')} <b>Features:</b>
{premium_emoji('✅')} 30 Days & 7 Days Trial
{premium_emoji('✅')} Auto Email + Password
{premium_emoji('✅')} Auto Email Checking
{premium_emoji('✅')} Email Content in Bot
{premium_emoji('✅')} Account Links

{premium_emoji('📝')} <b>How to use:</b>
{premium_emoji('1️⃣')} Choose trial type below
{premium_emoji('2️⃣')} Select Auto or Custom Email
{premium_emoji('3️⃣')} Get your trial!

{premium_emoji('👨‍💻')} <b>Owner:</b> {OWNER_CONTACT}

{premium_emoji('⬇️')} <b>Select an option:</b>
"""
    bot.send_message(chat_id, premium_emoji(welcome), reply_markup=create_main_menu(), parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    help_text = f"""
{premium_emoji('📖')} <b>Help & Commands</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('⚙️')} <b>Commands:</b>
/start - Main Menu
/help - This Help
/menu - Show Menu

{premium_emoji('🎯')} <b>How to Use:</b>
{premium_emoji('1️⃣')} Click "30 Days Trial" or "7 Days Trial"
{premium_emoji('2️⃣')} Choose "Auto Email" or "Custom Email"
{premium_emoji('3️⃣')} Get your trial!

{premium_emoji('📧')} <b>Email Options:</b>
{premium_emoji('🔄')} Auto - Bot creates temp email
{premium_emoji('✏️')} Custom - You provide email

{premium_emoji('⚠️')} <b>Limitations:</b>
• Max 5 per bulk
• 90 sec wait time

{premium_emoji('👨‍💻')} <b>Owner:</b> {OWNER_CONTACT}
"""
    bot.send_message(chat_id, premium_emoji(help_text), parse_mode='HTML', reply_markup=create_main_menu())

# ============================================
# 📩 HANDLERS
# ============================================
user_data = {}

def get_custom_email(message, days):
    chat_id = message.chat.id
    email = message.text.strip()
    
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        threading.Thread(target=process_custom_email, args=(chat_id, email, days), daemon=True).start()
    else:
        bot.send_message(chat_id, f"{premium_emoji('❌')} Invalid email! Send valid email:")
        bot.register_next_step_handler(message, get_custom_email, days)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        chat_id = call.message.chat.id
        data = call.data
        
        if data == "cancel":
            bot.edit_message_text(f"{premium_emoji('❌')} Cancelled.", chat_id, call.message.message_id)
            bot.send_message(chat_id, f"{premium_emoji('🏠')} Main Menu:", reply_markup=create_main_menu())
            return
        
        if data.startswith("auto_"):
            days = data.split("_")[1]
            bot.edit_message_text(f"{premium_emoji('⏳')} Processing {days} Days Trial...", chat_id, call.message.message_id)
            threading.Thread(target=process_auto_email, args=(chat_id, days), daemon=True).start()
            return
        
        if data.startswith("custom_"):
            days = data.split("_")[1]
            bot.edit_message_text(f"{premium_emoji('✏️')} Send your email for {days} Days Trial:", chat_id, call.message.message_id)
            bot.register_next_step_handler(call.message, get_custom_email, days)
            return
        
        if data.startswith("bulk_"):
            count = int(data.split("_")[1])
            bot.edit_message_text(f"{premium_emoji('⏳')} Generating {count} trials...", chat_id, call.message.message_id)
            threading.Thread(target=process_bulk_emails, args=(chat_id, count), daemon=True).start()
            return
            
    except Exception as e:
        print(f"Callback error: {e}")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    if text == "🎬 30 Days Trial":
        markup = create_email_type_buttons("30")
        bot.send_message(chat_id, f"{premium_emoji('📌')} Select email type for 30 Days Trial:", reply_markup=markup)
        return
    
    elif text == "⚡ 7 Days Trial":
        markup = create_email_type_buttons("7")
        bot.send_message(chat_id, f"{premium_emoji('📌')} Select email type for 7 Days Trial:", reply_markup=markup)
        return
    
    elif text == "✏️ Custom Email":
        bot.send_message(chat_id, f"{premium_emoji('✏️')} Send your email address:\n\nExample: <code>myemail@gmail.com</code>", parse_mode='HTML')
        bot.register_next_step_handler(message, get_custom_email, "7")
        return
    
    elif text == "📊 Bulk Generate":
        bot.send_message(chat_id, f"{premium_emoji('📊')} Select number of trials (1-5):", reply_markup=create_bulk_buttons())
        return
    
    elif text == "ℹ️ Help":
        help_command(message)
        return
    
    elif text == "👨‍💻 Owner":
        owner_text = f"""
{premium_emoji('👨‍💻')} <b>Bot Owner</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{premium_emoji('📛')} <b>Username:</b> {OWNER_USERNAME}
{premium_emoji('🆔')} <b>User ID:</b> {OWNER_ID}
{premium_emoji('📞')} <b>Contact:</b> {OWNER_CONTACT}

💌 For any issues or queries, contact directly.
"""
        bot.send_message(chat_id, premium_emoji(owner_text), parse_mode='HTML')
        return
    
    else:
        bot.send_message(chat_id, f"{premium_emoji('❌')} Use /start for menu.", reply_markup=create_main_menu())

# ============================================
# 🚀 START BOT
# ============================================
def signal_handler(sig, frame):
    print("\n🛑 Bot stopped by user!")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def start_bot():
    print("🔥" + "="*50)
    print("🔥  NETFLIX TRIAL BOT - PC FIXED")
    print("🔥" + "="*50)
    
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot: @{bot_info.username}")
        print(f"🤖 Name: {bot_info.first_name}")
        print(f"💻 System: {sys.platform}")
        print(f"🐍 Python: {sys.version}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n✅ Bot Running with PC Fixes!")
    print("📌 Features:")
    print("  • Main Menu Keyboard")
    print("  • Interactive Buttons")
    print("  • Auto & Custom Email")
    print("  • Bulk Generation")
    print("  • Premium Emojis")
    print("  • SSL/Encoding Fixed for PC")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️ Bot error: {e}")
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_bot()
    except KeyboardInterrupt:
        print("\n👋 Bye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)