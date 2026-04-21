import streamlit as st
import feedparser
import requests
import re
import urllib.parse
import time
import calendar
from datetime import datetime, timezone, timedelta

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="موجة نيوز", layout="wide", page_icon="📰")

# --- 2. التصميم الاحترافي (CSS) ---
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, div {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* 🎯 حيلة الاستقامة المليمترية للنص مع الدائرة */
    .align-font-label {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        height: 85px; /* ارتفاع مدروس ليتقاطع مع السلايدر */
        margin-top: -15px; /* رفع النص للأعلى */
    }

    .news-card { 
        background-color: #1E1E1E; 
        border-radius: 15px; 
        padding: 20px; 
        margin-bottom: 25px; 
        border: 1px solid #333;
    }
    
    .read-more-btn { 
        background-color: #1f77b4; color: white !important; 
        padding: 8px 20px; text-decoration: none; border-radius: 8px; 
        display: inline-block; font-weight: bold; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. جلب الأخبار بتوقيت بغداد ---
if "news_items" not in st.session_state:
    st.session_state.news_items = []

def fetch_news():
    url = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:30]:
            pub = entry.get('published_parsed')
            dt_str = ""
            if pub:
                # تحويل الوقت لـ GMT+3 (العراق)
                dt = datetime.fromtimestamp(calendar.timegm(pub), tz=timezone.utc).astimezone(timezone(timedelta(hours=3)))
                dt_str = dt.strftime('%I:%M %p | %Y/%m/%d')
            
            img = next((l.href for l in entry.get('links', []) if 'image' in l.type), None)
            if not img and 'media_content' in entry: img = entry.media_content[0].get('url')
            
            items.append({
                "title": re.sub('<.*?>', '', entry.title),
                "link": entry.link,
                "desc": re.sub('<.*?>', '', entry.get('description', '')),
                "date": dt_str,
                "img": img,
                "id": entry.get('id', entry.link)
            })
        st.session_state.news_items = items
    except: pass

fetch_news()

# --- 4. الواجهة العلوية (الاستقامة المليمترية) ---
# عمود العنوان - عمود فارغ للتوسيع - عمود التسمية - عمود السلايدر
col_logo, _, col_label, col_slider = st.columns([3, 0.2, 0.4, 1.4], vertical_alignment="center")

with col_logo:
    st.markdown("<h1 style='color: #4FA3E3; margin:0; padding:0;'>📰 منصة موجة نيوز</h1>", unsafe_allow_html=True)

with col_label:
    # استخدام كلاس align-font-label لرفع النص لمستوى الدائرة
    st.markdown("<div class='align-font-label'><p style='font-weight:bold; font-size:16px; margin:0;'>حجم الخط</p></div>", unsafe_allow_html=True)

with col_slider:
    f_size = st.select_slider("slider", options=range(16, 41), value=22, label_visibility="collapsed")

st.success("✅ تم التحقق من الهوية بنجاح. أهلاً بك في غرفة الأخبار.")

# --- 5. أداة استخراج الصور ---
with st.expander("📸 استخراج صورة من منصة X"):
    tweet_url = st.text_input("رابط التغريدة")
    if st.button("التقاط"):
        api_url = f"https://api.apiflash.com/v1/urltoimage?access_key=85706f41977042d3b642677a65d0d81c&url={urllib.parse.quote(tweet_url)}&element={urllib.parse.quote('article[data-testid=\"tweet\"]')}&delay=5"
        st.image(api_url)

st.markdown("---")

# --- 6. عرض الأخبار ---
for item in st.session_state.news_items:
    img_url = item['img'] if item['img'] else "https://via.placeholder.com/350x250?text=Mawja+News"
    
    with st.container():
        col_text, col_img = st.columns([2, 1])
        
        with col_img:
            st.image(img_url, use_container_width=True)
            # زر التحميل تحت الصورة مباشرة وبنفس العرض
            try:
                img_data = requests.get(img_url).content
                st.download_button(label="📥 تحميل الصورة", data=img_data, file_name=f"news_{int(time.time())}.jpg", mime="image/jpeg", key=f"dl_{item['id']}", use_container_width=True)
            except: pass
            
        with col_text:
            st.markdown(f"<div style='font-size:{f_size}px; font-weight:bold; color:#FFDF00; margin-bottom:5px;'>{item['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#87CEEB; font-size:14px; margin-bottom:10px;'>{item['date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:{max(14, f_size-6)}px; color:#ddd; line-height:1.6;'>{item['desc']}</p>", unsafe_allow_html=True)
            st.markdown(f"<a href='{item['link']}' target='_blank' class='read-more-btn'>فتح الرابط الأصلي 🔗</a>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border: 0.5px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)

time.sleep(120)
st.rerun()
