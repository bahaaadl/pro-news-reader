import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone, timedelta
import calendar
import re
import html
import time
import urllib.parse

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="موجة نيوز", layout="wide", page_icon="📰")

# --- 2. التصميم (CSS) ---
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    
    .news-card { 
        display: flex; flex-direction: row; background-color: #1E1E1E; 
        border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid #444; 
    }
    .news-content { flex: 1; padding-left: 20px; text-align: right; }
    .news-image-container { width: 250px; height: 250px; flex-shrink: 0; border-radius: 10px; overflow: hidden; }
    .news-image-container img { width: 100%; height: 100%; object-fit: cover; }
    .read-more-btn { 
        background-color: #1f77b4; color: white !important; padding: 8px 15px; 
        text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 10px;
    }
    @media (max-width: 768px) {
        .news-card { flex-direction: column; }
        .news-image-container { width: 100%; height: auto; min-height: 200px; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. وظائف جلب الأخبار ---
if "news_items" not in st.session_state: st.session_state.news_items = []

def fetch_news():
    url = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:30]:
            img = next((l.href for l in entry.get('links', []) if 'image' in l.type), None)
            if not img and 'media_content' in entry: img = entry.media_content[0].get('url')
            
            items.append({
                "title": re.sub('<.*?>', '', entry.title),
                "link": entry.link,
                "desc": re.sub('<.*?>', '', entry.get('description', '')),
                "img": img
            })
        st.session_state.news_items = items
    except: pass

fetch_news()

# --- 4. الواجهة العلوية ---
col_t, col_s = st.columns([3, 1])
with col_t: st.markdown("<h2 style='color: #4FA3E3;'>📰 منصة موجة نيوز</h2>", unsafe_allow_html=True)
with col_s: f_size = st.slider("حجم الخط", 15, 40, 22)

st.success("✅ تم التحقق من الهوية بنجاح. أهلاً بك في غرفة الأخبار.")

# --- 5. أداة التقاط الصور ---
with st.expander("📸 استخراج صورة من X"):
    tweet_url = st.text_input("رابط التغريدة")
    if st.button("التقط"):
        api_url = f"https://api.apiflash.com/v1/urltoimage?access_key=85706f41977042d3b642677a65d0d81c&url={urllib.parse.quote(tweet_url)}&element={urllib.parse.quote('article[data-testid=\"tweet\"]')}&delay=5"
        st.image(api_url)

# --- 6. عرض الأخبار بتنسيق البطاقات الصحيح ---
for item in st.session_state.news_items:
    img_html = f"<img src='{item['img']}'>" if item['img'] else "<div style='height:250px; background:#333;'></div>"
    
    # بناء البطاقة باستخدام Markdown واحد لضمان عدم تداخل الأكواد
    card_html = f"""
    <div class="news-card">
        <div class="news-content">
            <div style="font-size:{f_size}px; font-weight:bold; color:white; margin-bottom:10px;">{item['title']}</div>
            <p style="font-size:{max(12, f_size-6)}px; color:#ccc;">{item['desc']}</p>
            <a href="{item['link']}" target="_blank" class="read-more-btn">فتح الرابط 🔗</a>
        </div>
        <div class="news-image-container">
            {img_html}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# تحديث تلقائي بسيط
time.sleep(60)
st.rerun()
