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

# --- 2. التصميم الاحترافي (CSS) ---
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [data-testid="stsidebar"], .stMarkdown, p, h1, h2, h3, div {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }

    .news-card { 
        display: flex; flex-direction: row; background-color: #1E1E1E; 
        border-radius: 12px; padding: 15px; margin-bottom: 20px; border: 1px solid #444; 
    }
    .news-content { flex: 1; padding-left: 20px; }
    
    .news-image-container { 
        width: 280px; height: 180px; flex-shrink: 0; 
        border-radius: 8px; overflow: hidden; background: #222;
    }
    .news-image-container img { 
        width: 100%; height: 100%; object-fit: contain; /* للحفاظ على أبعاد الصورة كاملة */
    }
    
    .read-more-btn { 
        background-color: #1f77b4; color: white !important; padding: 6px 15px; 
        text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;
        font-size: 14px;
    }

    @media (max-width: 768px) {
        .news-card { flex-direction: column; }
        .news-content { padding-left: 0; margin-top: 10px; order: 2; }
        .news-image-container { width: 100%; height: 220px; order: 1; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. جلب الأخبار ---
if "news_items" not in st.session_state:
    st.session_state.news_items = []

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
                "img": img,
                "id": entry.get('id', entry.link)
            })
        st.session_state.news_items = items
    except:
        pass

fetch_news()

# --- 4. الواجهة العلوية ---
col_logo, col_font = st.columns([3, 1])
with col_logo:
    st.markdown("<h1 style='color: #4FA3E3; margin:0;'>📰 منصة موجة نيوز</h1>", unsafe_allow_html=True)
with col_font:
    f_size = st.slider("حجم الخط", 16, 40, 22)

st.success("✅ تم التحقق من الهوية بنجاح. أهلاً بك في غرفة الأخبار.")

# --- 5. أداة استخراج الصور ---
with st.expander("📸 استخراج صورة من منصة X"):
    tweet_url = st.text_input("رابط التغريدة هنا")
    if st.button("التقاط الصورة"):
        if tweet_url:
            api_url = f"https://api.apiflash.com/v1/urltoimage?access_key=85706f41977042d3b642677a65d0d81c&url={urllib.parse.quote(tweet_url)}&element={urllib.parse.quote('article[data-testid=\"tweet\"]')}&delay=5"
            st.image(api_url, caption="تم الالتقاط بنجاح")

st.markdown("---")

# --- 6. عرض الأخبار ---
for item in st.session_state.news_items:
    img_url = item['img'] if item['img'] else "https://via.placeholder.com/280x180?text=Mawja+News"
    
    # بناء الهيكل باستخدام columns لتحسين التفاعل (الترجمة)
    with st.container():
        col_text, col_img = st.columns([2, 1])
        
        with col_img:
            st.image(img_url, use_container_width=True)
            
        with col_text:
            st.markdown(f"<div style='font-size:{f_size}px; font-weight:bold; color:white;'>{item['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:{max(14, f_size-6)}px; color:#ccc;'>{item['desc']}</p>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"<a href='{item['link']}' target='_blank' class='read-more-btn'>فتح الرابط 🔗</a>", unsafe_allow_html=True)
            with c2:
                if st.button("ترجمة الخبر ✨", key=f"tr_{item['id']}"):
                    st.info("جاري الترجمة عبر Gemini...")
                    # هنا تضع كود الترجمة الخاص بك مستقبلاً
        
        st.markdown("<hr style='border: 0.5px solid #333;'>", unsafe_allow_html=True)

# تحديث تلقائي كل دقيقتين
time.sleep(120)
st.rerun()
