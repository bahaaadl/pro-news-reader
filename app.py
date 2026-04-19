import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone, timedelta
import calendar
import re
import html
import time
import base64
from streamlit_cookies_manager import EncryptedCookieManager

# --- إعداد مدير ملفات تعريف الارتباط (Cookies) ---
# ملاحظة: اختر كلمة سر عشوائية لتشفير الكوكيز
cookies = EncryptedCookieManager(password="L6V299S8B1N0M3X4Z5Q6W7E8")
if not cookies.ready():
    st.stop()

# --- إعدادات صفحة الموقع ---
st.set_page_config(page_title="قارئ الأخبار الاحترافي", layout="wide", page_icon="📰")

# --- إخفاء شريط Streamlit العلوي ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', Arial, sans-serif; }
.news-card { display: flex; flex-direction: row; direction: rtl; background-color: #1E1E1E; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid #444444; }
.news-card.new-item { animation: pulse-border 2s infinite; }
@keyframes pulse-border { 0% { border-color: #FFDF00; } 50% { border-color: #B8860B; } 100% { border-color: #FFDF00; } }
.news-content { flex: 1; padding-left: 20px; text-align: right; }
.news-image-container { width: 250px; height: 250px; flex-shrink: 0; border-radius: 10px; overflow: hidden; border: 1px solid #333; display: flex; align-items: center; justify-content: center; }
.news-image-container img { width: 100%; height: 100%; object-fit: cover; }
.read-more-btn { background-color: #1f77b4; color: white !important; padding: 8px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; display: inline-block; }
.download-btn { background-color: #28a745; color: white !important; padding: 8px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; margin-right: 10px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- فحص حالة تسجيل الدخول من الكوكيز ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = cookies.get("is_logged_in") == "true"

# --- شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔒 منصة الأخبار الاحترافية</h1><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div dir='rtl'>", unsafe_allow_html=True)
        user = st.text_input("اسم المستخدم")
        pwd = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول", use_container_width=True):
            if user == "admin" and pwd == "1234":
                st.session_state.logged_in = True
                cookies["is_logged_in"] = "true"
                cookies.save() # حفظ الكوكيز في المتصفح
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- خيار تسجيل الخروج (اختياري) ---
if st.sidebar.button("تسجيل الخروج 🚪"):
    st.session_state.logged_in = False
    cookies["is_logged_in"] = "false"
    cookies.save()
    st.rerun()

# --- باقي كود سحب الأخبار والعرض (كما هو في الكود السابق) ---
# ... (دوال fetch_news و clean_text_safe و get_image_bytes) ...

if "seen_links" not in st.session_state: st.session_state.seen_links = set()
if "font_size" not in st.session_state: st.session_state.font_size = 22
if "news_items" not in st.session_state: st.session_state.news_items = []

@st.cache_data(show_spinner=False)
def get_image_bytes(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        return response.content if response.status_code == 200 else None
    except: return None

def clean_text_safe(raw_html):
    if not raw_html: return ""
    clean = re.sub('<.*?>', '', raw_html)
    return html.escape(html.unescape(clean.strip()).replace('\n', ' '))

def fetch_news():
    url = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"
    try:
        feed = feedparser.parse(url)
        new_items = []
        is_first_load = len(st.session_state.news_items) == 0
        for item in st.session_state.news_items: item["is_new"] = False
        entries = feed.entries[:50]
        if not is_first_load: entries.reverse()
        for entry in entries:
            if entry.link not in st.session_state.seen_links:
                pub = entry.get('published_parsed')
                dt_str = ""
                if pub:
                    dt = datetime.fromtimestamp(calendar.timegm(pub), tz=timezone.utc).astimezone(timezone(timedelta(hours=3)))
                    dt_str = f"التوقيت: {dt.strftime('%I:%M %p')} | التاريخ: {dt.strftime('%Y/%m/%d')}"
                img_url = next((l.href for l in entry.get('links', []) if 'image' in l.type), None)
                if not img_url and 'media_content' in entry: img_url = entry.media_content[0].get('url')
                new_items.append({
                    "title": clean_text_safe(entry.title), "link": entry.link,
                    "desc": clean_text_safe(entry.get('description', '')), "date": dt_str,
                    "img": img_url, "is_new": not is_first_load 
                })
                st.session_state.seen_links.add(entry.link)
        if new_items:
            if is_first_load: new_items.reverse()
            st.session_state.news_items = new_items + st.session_state.news_items
    except: pass

st.session_state.font_size = st.sidebar.slider("حجم الخط", 15, 50, st.session_state.font_size)
fetch_news()

for item in st.session_state.news_items:
    card_class = "news-card new-item" if item["is_new"] else "news-card"
    new_badge = "<div style='color: #FFDF00; font-weight: bold; font-size: 18px; margin-bottom: 10px;'>⭐ جديد</div>" if item["is_new"] else ""
    img_content = "لا توجد صورة"
    download_btn = ""
    if item['img']:
        img_bytes = get_image_bytes(item['img'])
        if img_bytes:
            b64_img = base64.b64encode(img_bytes).decode('utf-8')
            img_src = f"data:image/jpeg;base64,{b64_img}"
            img_content = f"<img src='{img_src}'>"
            download_btn = f"<a href='{img_src}' download='news_img.jpg' class='download-btn'>تنزيل الصورة 📥</a>"
    card_html = f"<div class='{card_class}'><div class='news-content'>{new_badge}<div style='font-size: {st.session_state.font_size}px; font-weight: bold; color: white;'>{item['title']}</div><div style='font-size: 14px; color: #87CEEB;'>{item['date']}</div><div style='font-size: {max(14, st.session_state.font_size - 6)}px; color: #cccccc;'>{item['desc']}</div><div style='display: flex; gap: 10px;'><a href='{item['link']}' target='_blank' class='read-more-btn'>قراءة الخبر 🔗</a>{download_btn}</div></div><div class='news-image-container'>{img_content}</div></div>"
    st.markdown("".join([line.strip() for line in card_html.split('\n')]), unsafe_allow_html=True)

time.sleep(5)
st.rerun()
