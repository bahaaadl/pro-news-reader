import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone, timedelta
import calendar
import re
import html
import time
import urllib.parse
import json
import os
from datetime import date

# --- 1. إعدادات الصفحة (يجب أن يكون أول أمر) ---
st.set_page_config(page_title="موجة نيوز - غرفة الأخبار", layout="wide", page_icon="📰")

# --- 2. كود التصميم والتنسيق (CSS) ---
st.markdown("""
<style>
/* إخفاء قوائم ستريمليت نهائياً */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stAppDeployButton {display:none;}
[data-testid="stStatusWidget"] {display:none;}

/* إعدادات الخط العربي */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; }

/* تصميم بطاقات الأخبار */
.news-card { 
    display: flex; flex-direction: row; direction: rtl; 
    background-color: #1E1E1E; border-radius: 12px; 
    padding: 20px; margin-bottom: 20px; border: 2px solid #444444; 
}
.news-card.new-item { animation: pulse-border 2s infinite; }
@keyframes pulse-border { 0% { border-color: #FFDF00; } 50% { border-color: #B8860B; } 100% { border-color: #FFDF00; } }
.news-content { flex: 1; padding-left: 20px; text-align: right; }
.news-image-container { width: 250px; height: 250px; flex-shrink: 0; border-radius: 10px; overflow: hidden; border: 1px solid #333; }
.news-image-container img { width: 100%; height: 100%; object-fit: cover; }
.read-more-btn { background-color: #1f77b4; color: white !important; padding: 8px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; display: inline-block; }

/* الموبايل */
@media (max-width: 768px) {
    .news-card { flex-direction: column; padding: 15px; }
    .news-content { padding-left: 0; margin-bottom: 15px; }
    .news-image-container { width: 100%; height: auto; min-height: 200px; }
}
</style>
""", unsafe_allow_html=True)

# --- 3. وظائف النظام ---
def play_notification_sound():
    sound_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    html_str = f'<audio autoplay style="display:none;"><source src="{sound_url}" type="audio/mp3"></audio>'
    st.components.v1.html(html_str, height=0)

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
                new_entries.append({
                    "title": html.escape(re.sub('<.*?>', '', entry.title)),
                    "link": entry.link, "desc": html.escape(re.sub('<.*?>', '', entry.get('description', ''))),
                    "date": dt_str, "img": img, "is_new": not is_first
                })
                st.session_state.seen_links.add(entry.link)
        if new_entries:
            if not is_first:
                st.toast(f"🔔 {len(new_entries)} أخبار جديدة!", icon="🆕")
                play_notification_sound()
            st.session_state.news_items = new_entries + st.session_state.news_items
    except: pass

fetch_news()

# --- 4. واجهة المستخدم ---
col_t, col_s = st.columns([3, 1])
with col_t: st.markdown("<h2 style='color: #4FA3E3;'>📰 منصة موجة نيوز</h2>", unsafe_allow_html=True)
with col_s: f_size = st.slider("حجم الخط", 15, 50, 22)

st.success("✅ تم التحقق من الهوية بنجاح. أهلاً بك في غرفة الأخبار.")

# --- 5. أداة التقاط الصور (X Capture) ---
st.subheader("📸 استخراج صورة من X")
if "snapshot_img" not in st.session_state: st.session_state.snapshot_img = None

with st.expander("فتح أداة الالتقاط"):
    tweet_url = st.text_input("رابط التغريدة")
    if st.button("التقط") and tweet_url:
        with st.spinner("جاري الالتقاط..."):
            api_url = f"https://api.apiflash.com/v1/urltoimage?access_key=85706f41977042d3b642677a65d0d81c&url={urllib.parse.quote(tweet_url)}&element={urllib.parse.quote('article[data-testid=\"tweet\"]')}&delay=5"
            resp = requests.get(api_url)
            if resp.status_code == 200:
                st.session_state.snapshot_img = resp.content
                st.rerun()

if st.session_state.snapshot_img:
    st.image(st.session_state.snapshot_img)
    if st.button("إغلاق الصورة"):
        st.session_state.snapshot_img = None
        st.rerun()

st.markdown("---")

# --- 6. عرض الأخبار ---
for item in st.session_state.news_items:
    card_class = "news-card new-item" if item["is_new"] else "news-card"
    badge = "<div style='color:#FFDF00; font-weight:bold;'>⭐ جديد</div>" if item["is_new"] else ""
    img_tag = f"<img src='{item['img']}'>" if item['img'] else ""
    
    html_content = f"""
    <div class='{card_class}'>
        <div class='news-content'>
            {badge}
            <div style='font-size:{f_size}px; font-weight:bold;'>{item['title']}</div>
            <div style='color:#87CEEB; font-size:14px;'>{item['date']}</div>
            <p style='font-size:{max(12, f_size-6)}px; color:#ccc;'>{item['desc']}</p>
            <a href='{item['link']}' target='_blank' class='read-more-btn'>فتح الرابط 🔗</a>
        </div>
        <div class='news-image-container'>{img_tag}</div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

time.sleep(30)
st.rerun()
