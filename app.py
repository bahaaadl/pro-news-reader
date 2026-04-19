import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone, timedelta
import calendar
import re
import html
import time
import base64

# --- إعدادات صفحة الموقع ---
st.set_page_config(page_title="قارئ الأخبار الاحترافي", layout="wide", page_icon="📰")

# --- دالة تحميل الصور وتشفيرها (لتخطي الحماية) ---
@st.cache_data(show_spinner=False)
def get_image_bytes(url):
    try:
        # إضافة User-Agent لكي يظن المصدر أننا متصفح حقيقي وليس روبوت
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None

# --- كود CSS الاحترافي ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}

@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');

* {
    font-family: 'Tajawal', Arial, sans-serif;
}

.news-card {
    display: flex;
    flex-direction: row;
    direction: rtl;
    background-color: #1E1E1E;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    border: 2px solid #444444; 
    transition: all 0.3s ease;
}

.news-card.new-item {
    animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
    0% { border-color: #FFDF00; box-shadow: 0 0 5px rgba(255, 223, 0, 0.2); }
    50% { border-color: #B8860B; box-shadow: 0 0 15px rgba(218, 165, 32, 0.6); }
    100% { border-color: #FFDF00; box-shadow: 0 0 5px rgba(255, 223, 0, 0.2); }
}

.news-content {
    flex: 1;
    padding-left: 20px;
    text-align: right;
}

.news-image-container {
    width: 250px;
    height: 250px;
    flex-shrink: 0;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #333;
    background-color: #2b2b2b;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #888;
    font-weight: bold;
}

.news-image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.read-more-btn {
    background-color: #1f77b4;
    color: white !important;
    padding: 8px 20px;
    text-decoration: none;
    border-radius: 6px;
    font-weight: bold;
    font-size: 16px;
    display: inline-block;
    margin-top: 10px;
    transition: 0.3s;
}

.read-more-btn:hover {
    background-color: #155a8a;
}

.download-btn {
    background-color: #28a745;
    color: white !important;
    padding: 8px 20px;
    text-decoration: none;
    border-radius: 6px;
    font-weight: bold;
    font-size: 16px;
    display: inline-block;
    margin-top: 10px;
    margin-right: 10px;
    transition: 0.3s;
}

.download-btn:hover {
    background-color: #218838;
}

@media (max-width: 768px) {
    .news-card {
        flex-direction: column-reverse;
    }
    .news-content {
        padding-left: 0;
        margin-top: 15px;
    }
    .news-image-container {
        width: 100%;
        height: 200px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- تهيئة الذاكرة المؤقتة ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "seen_links" not in st.session_state: st.session_state.seen_links = set()
if "font_size" not in st.session_state: st.session_state.font_size = 22
if "news_items" not in st.session_state: st.session_state.news_items = []

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
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- دالة التنظيف والتشفير الجذري ---
def clean_text_safe(raw_html):
    if not raw_html: return ""
    clean = re.sub('<.*?>', '', raw_html)
    clean = html.unescape(clean.strip()).replace('\n', ' ').replace('\r', ' ')
    return html.escape(clean)

# --- معالجة وسحب الأخبار ---
def fetch_news():
    url = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"
    try:
        feed = feedparser.parse(url)
        new_items = []
        entries = feed.entries[:50]
        
        is_first_load = len(st.session_state.news_items) == 0
        
        for item in st.session_state.news_items:
            item["is_new"] = False

        if not is_first_load:
            entries.reverse()
            
        for entry in entries:
            if entry.link not in st.session_state.seen_links:
                pub = entry.get('published_parsed') or entry.get('updated_parsed')
                dt_str = "تاريخ النشر غير متوفر"
                if pub:
                    dt = datetime.fromtimestamp(calendar.timegm(pub), tz=timezone.utc).astimezone(timezone(timedelta(hours=3)))
                    ampm = "م" if dt.hour >= 12 else "ص"
                    h12 = dt.hour % 12 or 12
                    dt_str = f"التوقيت: {h12:02d}:{dt.minute:02d} {ampm} | التاريخ: {dt.strftime('%Y/%m/%d')}"

                img_url = next((l.href for l in entry.get('links', []) if 'image' in l.type), None)
                if not img_url and 'media_content' in entry: img_url = entry.media_content[0].get('url')

                new_items.append({
                    "title": clean_text_safe(entry.title),
                    "link": entry.link,
                    "desc": clean_text_safe(entry.get('description', '')),
                    "date": dt_str,
                    "img": img_url,
                    "is_new": not is_first_load 
                })
                st.session_state.seen_links.add(entry.link)

        if new_items:
            if is_first_load: new_items.reverse()
            st.session_state.news_items = new_items + st.session_state.news_items
    except:
        pass

# --- الواجهة الرئيسية للموقع ---
col_space, col_slider = st.columns([3, 1])
with col_slider:
    st.session_state.font_size = st.slider("حجم الخط", 15, 50, st.session_state.font_size)

st.markdown("<hr>", unsafe_allow_html=True)

fetch_news()

# --- رسم الأخبار بضمان 100% ---
for item in st.session_state.news_items:
    card_class = "news-card new-item" if item["is_new"] else "news-card"
    new_badge = "<div style='color: #FFDF00; font-weight: bold; font-size: 18px; margin-bottom: 10px;'>⭐ جديد</div>" if item["is_new"] else ""
    
    img_content = "لا توجد صورة"
    download_btn = ""

    # تحويل الصورة إلى Base64 وزرعها مباشرة في الكود لتخطي الحماية
    if item['img']:
        img_bytes = get_image_bytes(item['img'])
        if img_bytes:
            b64_img = base64.b64encode(img_bytes).decode('utf-8')
            img_src = f"data:image/jpeg;base64,{b64_img}"
            img_content = f"<img src='{img_src}'>"
            
            # زر تنزيل مبني بـ HTML ليظهر داخل البطاقة لونه أخضر أنيق
            download_btn = f"<a href='{img_src}' download='news_image_{int(time.time())}.jpg' class='download-btn'>تنزيل الصورة 📥</a>"

    card_html = f"""
    <div class="{card_class}">
        <div class="news-content">
            {new_badge}
            <div style="font-size: {st.session_state.font_size}px; font-weight: bold; color: white; line-height: 1.4; margin-bottom: 5px;">{item['title']}</div>
            <div style="font-size: 14px; color: #87CEEB; margin-bottom: 15px;">{item['date']}</div>
            <div style="font-size: {max(14, st.session_state.font_size - 6)}px; color: #cccccc; line-height: 1.6; margin-bottom: 15px;">{item['desc']}</div>
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <a href="{item['link']}" target="_blank" class="read-more-btn">قراءة الخبر كاملاً 🔗</a>
                {download_btn}
            </div>
        </div>
        <div class="news-image-container">
            {img_content}
        </div>
    </div>
    """
    
    # دمج النص لإجبار المتصفح على قراءته كتصميم
    safe_html = "".join([line.strip() for line in card_html.split('\n')])
    st.markdown(safe_html, unsafe_allow_html=True)

# التحديث التلقائي الصامت كل 5 ثوانٍ
time.sleep(5)
st.rerun()
