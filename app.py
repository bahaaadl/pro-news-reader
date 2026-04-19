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

# --- إعداد الكوكيز ---
cookies = EncryptedCookieManager(password="L6V299S8B1N0M3X4Z5Q6W7E8")
if not cookies.ready():
    st.stop()

# --- إعدادات الصفحة ---
st.set_page_config(page_title="قارئ الأخبار الاحترافي", layout="wide", page_icon="📰")

# --- دالة لتشغيل صوت التنبيه ---
def play_notification_sound():
    # رابط لصوت تنبيه خفيف (Notification sound)
    sound_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    html_str = f"""
        <audio autoplay style="display:none;">
            <source src="{sound_url}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(html_str, height=0)

# --- CSS المحسن ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; }
.news-card { display: flex; flex-direction: row; direction: rtl; background-color: #1E1E1E; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid #444444; }
.news-card.new-item { animation: pulse-border 2s infinite; }
@keyframes pulse-border { 0% { border-color: #FFDF00; } 50% { border-color: #B8860B; } 100% { border-color: #FFDF00; } }
.news-content { flex: 1; padding-left: 20px; text-align: right; }
.news-image-container { width: 250px; height: 250px; flex-shrink: 0; border-radius: 10px; overflow: hidden; border: 1px solid #333; }
.news-image-container img { width: 100%; height: 100%; object-fit: cover; }
.read-more-btn { background-color: #1f77b4; color: white !important; padding: 8px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- تسجيل الدخول ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = cookies.get("is_logged_in") == "true"

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔒 دخول النظام</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول", use_container_width=True):
            if u == "admin" and p == "1234":
                st.session_state.logged_in = True
                cookies["is_logged_in"] = "true"
                cookies.save()
                st.rerun()
            else: st.error("خطأ!")
    st.stop()

# --- جلب الأخبار مع منطق التنبيه ---
if "seen_links" not in st.session_state: st.session_state.seen_links = set()
if "news_items" not in st.session_state: st.session_state.news_items = []

def fetch_news():
    url = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"
    try:
        feed = feedparser.parse(url)
        new_entries = []
        is_first = len(st.session_state.news_items) == 0
        
        for item in st.session_state.news_items: item["is_new"] = False
        
        for entry in feed.entries[:50]:
            if entry.link not in st.session_state.seen_links:
                pub = entry.get('published_parsed')
                dt_str = ""
                if pub:
                    dt = datetime.fromtimestamp(calendar.timegm(pub), tz=timezone.utc).astimezone(timezone(timedelta(hours=3)))
                    dt_str = dt.strftime('%I:%M %p | %Y/%m/%d')
                
                img = next((l.href for l in entry.get('links', []) if 'image' in l.type), None)
                if not img and 'media_content' in entry: img = entry.media_content[0].get('url')
                
                clean_title = re.sub('<.*?>', '', entry.title).replace('\n', ' ')
                clean_desc = re.sub('<.*?>', '', entry.get('description', '')).replace('\n', ' ')
                
                new_entries.append({
                    "title": html.escape(clean_title), "link": entry.link, "desc": html.escape(clean_desc),
                    "date": dt_str, "img": img, "is_new": not is_first
                })
                st.session_state.seen_links.add(entry.link)
        
        if new_entries:
            # إذا لم تكن المرة الأولى، أطلق التنبيهات
            if not is_first:
                st.toast(f"🔔 تم استلام {len(new_entries)} أخبار جديدة!", icon="🆕")
                play_notification_sound()
            
            st.session_state.news_items = new_entries + st.session_state.news_items
    except: pass

fetch_news()

# --- واجهة العرض ---
st.sidebar.title("الإعدادات")
f_size = st.sidebar.slider("حجم الخط", 15, 50, 22)
if st.sidebar.button("خروج"):
    cookies["is_logged_in"] = "false"; cookies.save()
    st.session_state.logged_in = False; st.rerun()

for item in st.session_state.news_items:
    card_class = "news-card new-item" if item["is_new"] else "news-card"
    badge = "<div style='color:#FFDF00; font-weight:bold;'>⭐ جديد</div>" if item["is_new"] else ""
    img_tag = f"<img src='{item['img']}'>" if item['img'] else "لا توجد صورة"
    
    html_content = f"<div class='{card_class}'><div class='news-content'>{badge}<div style='font-size:{f_size}px; font-weight:bold; color:white;'>{item['title']}</div><div style='color:#87CEEB; font-size:14px;'>{item['date']}</div><div style='font-size:{max(12, f_size-6)}px; color:#ccc; margin:10px 0;'>{item['desc']}</div><a href='{item['link']}' target='_blank' class='read-more-btn'>فتح الرابط 🔗</a></div><div class='news-image-container'>{img_tag}</div></div>"
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    if item['img']:
        try:
            st.download_button("تنزيل الصورة 📥", requests.get(item['img']).content, f"img_{int(time.time())}.jpg", "image/jpeg", key=item['link'])
        except: pass

time.sleep(10)
st.rerun()
