import streamlit as st
import feedparser
import requests
import re
import urllib.parse
import time

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="موجة نيوز", layout="wide", page_icon="📰")

# --- 2. التصميم (CSS) - النسخة الاحترافية النهائية ---
st.markdown("""
<style>
    /* إخفاء الزوائد */
    #MainMenu, header, footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* الخط والاتجاه العربي */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3 {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* تصميم البطاقة الذكي */
    .news-card { 
        display: flex; 
        flex-direction: row-reverse; 
        background-color: #1E1E1E; 
        border-radius: 15px; 
        margin-bottom: 25px; 
        border: 1px solid #333;
        overflow: hidden;
        height: 250px; /* طول ثابت للبطاقة لضمان التناسق */
    }
    
    .news-content { 
        flex: 2; 
        padding: 20px; 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
    }
    
    .news-image-container { 
        flex: 1;
        max-width: 350px;
        background: #000;
    }
    
    .news-image-container img { 
        width: 100%; 
        height: 100%; 
        object-fit: cover; /* يضمن ملء المساحة دون قص مشوه */
    }
    
    .read-more-btn { 
        background-color: #1f77b4; color: white !important; 
        padding: 8px 25px; text-decoration: none; border-radius: 8px; 
        font-weight: bold; width: fit-content;
    }

    /* التجاوب مع الموبايل */
    @media (max-width: 768px) {
        .news-card { flex-direction: column; height: auto; }
        .news-image-container { max-width: 100%; height: 200px; }
        .news-content { padding: 15px; }
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
                "img": img
            })
        st.session_state.news_items = items
    except: pass

fetch_news()

# --- 4. الهيدر (العنوان + حجم الخط) ---
# جعلنا الهيدر في سطر واحد كما في صورتك الأخيرة
col_title, col_font = st.columns([3, 1])
with col_title:
    st.markdown("<h1 style='color: #4FA3E3;'>📰 منصة موجة نيوز</h1>", unsafe_allow_html=True)
with col_font:
    f_size = st.select_slider("حجم الخط", options=range(16, 41), value=22)

st.success("✅ أهلاً بك في غرفة الأخبار.")

# --- 5. أداة استخراج الصور ---
with st.expander("📸 أداة استخراج صورة من X"):
    tweet_url = st.text_input("أدخل الرابط")
    if st.button("التقاط"):
        api_url = f"https://api.apiflash.com/v1/urltoimage?access_key=85706f41977042d3b642677a65d0d81c&url={urllib.parse.quote(tweet_url)}&element={urllib.parse.quote('article[data-testid=\"tweet\"]')}&delay=5"
        st.image(api_url)

st.markdown("---")

# --- 6. عرض الأخبار ---
for item in st.session_state.news_items:
    img_url = item['img'] if item['img'] else "https://via.placeholder.com/350x250?text=Mawja+News"
    
    card_html = f"""
    <div class="news-card">
        <div class="news-content">
            <div>
                <div style="font-size:{f_size}px; font-weight:bold; color:#FFDF00; margin-bottom:8px;">{item['title']}</div>
                <p style="font-size:{max(14, f_size-6)}px; color:#ddd; line-height:1.5;">{item['desc']}</p>
            </div>
            <a href="{item['link']}" target="_blank" class="read-more-btn">فتح الرابط 🔗</a>
        </div>
        <div class="news-image-container">
            <img src="{img_url}">
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# ريفرش هادئ كل دقيقتين
time.sleep(120)
st.rerun()
