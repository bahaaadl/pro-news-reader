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

# --- 2. التصميم (CSS) فقط بدون كود JS خارجي ---
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

    /* استقامة الهيدر */
    .align-font-label {
        display: flex; align-items: center; justify-content: flex-end;
        height: 100%; padding-top: 5px;
    }

    .news-card { 
        background-color: #1E1E1E; border-radius: 15px; 
        padding: 20px; margin-bottom: 25px; border: 1px solid #333;
    }
    
    /* تنسيق الأزرار بجانب بعضها */
    .btn-container {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }

    .read-more-btn { 
        background-color: #1f77b4; color: white !important; 
        padding: 8px 15px; text-decoration: none; border-radius: 8px; 
        font-weight: bold; font-size: 14px; display: inline-block;
    }

    .copy-btn {
        background-color: #2d2d2d; color: #4FA3E3 !important;
        padding: 8px 15px; border-radius: 8px; cursor: pointer;
        border: 1px solid #4FA3E3; font-weight: bold; font-size: 14px;
        display: flex; align-items: center; gap: 5px;
    }
    
    .copy-btn:hover { background-color: #4FA3E3; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. جلب الأخبار ---
if "news_items" not in st.session_state: st.session_state.news_items = []

def fetch_news():
    url = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:30]:
            pub = entry.get('published_parsed')
            dt_str = ""
            if pub:
                dt = datetime.fromtimestamp(calendar.timegm(pub), tz=timezone.utc).astimezone(timezone(timedelta(hours=3)))
                dt_str = dt.strftime('%I:%M %p | %Y/%m/%d')
            
            img = next((l.href for l in entry.get('links', []) if 'image' in l.type), None)
            if not img and 'media_content' in entry: img = entry.media_content[0].get('url')
            
            title = re.sub('<.*?>', '', entry.title).strip()
            desc = re.sub('<.*?>', '', entry.get('description', '')).strip()
            full_text = f"{title}\n\n{desc}"

            items.append({
                "title": title, "link": entry.link, "desc": desc,
                "date": dt_str, "img": img, 
                "id": "".join(filter(str.isalnum, entry.link[-10:])),
                "copy_text": full_text
            })
        st.session_state.news_items = items
    except: pass

fetch_news()

# --- 4. الواجهة العلوية ---
col_logo, _, col_label, col_slider = st.columns([3, 0.2, 0.4, 1.4], vertical_alignment="center")
with col_logo: st.markdown("<h1 style='color: #4FA3E3; margin:0;'>📰 منصة موجة نيوز</h1>", unsafe_allow_html=True)
with col_label: st.markdown("<div class='align-font-label'><p style='font-weight:bold; margin:0;'>حجم الخط</p></div>", unsafe_allow_html=True)
with col_slider: f_size = st.select_slider("slider", options=range(16, 41), value=22, label_visibility="collapsed")

st.success("✅ أهلاً بك في غرفة الأخبار.")
st.markdown("---")

# --- 5. عرض الأخبار ---
for item in st.session_state.news_items:
    img_url = item['img'] if item['img'] else "https://via.placeholder.com/350x250?text=Mawja+News"
    
    # تحويل النص بالكامل إلى كود آمن جداً للـ JavaScript
    encoded_text = urllib.parse.quote(item['copy_text'])
    
    with st.container():
        col_text, col_img = st.columns([2, 1])
        
        with col_img:
            st.image(img_url, use_container_width=True)
            try:
                img_data = requests.get(img_url).content
                st.download_button(label="📥 تحميل الصورة", data=img_data, file_name="news.jpg", mime="image/jpeg", key=f"dl_{item['id']}", use_container_width=True)
            except: pass
            
        with col_text:
            st.markdown(f"<div style='font-size:{f_size}px; font-weight:bold; color:#FFDF00;'>{item['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#87CEEB; font-size:14px; margin:5px 0;'>{item['date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:{max(14, f_size-6)}px; color:#ddd;'>{item['desc']}</p>", unsafe_allow_html=True)
            
            # زر النسخ مع كود الجافاسكريبت المدمج فيه مباشرة (يحل مشكلة Streamlit)
            html_btns = f"""
            <div class="btn-container">
                <a href="{item['link']}" target="_blank" class="read-more-btn">فتح الرابط 🔗</a>
                <div class="copy-btn" onclick="
                    var btn = this;
                    var txt = decodeURIComponent('{encoded_text}');
                    if (navigator.clipboard) {{
                        navigator.clipboard.writeText(txt).then(() => {{
                            btn.innerHTML = '✅ تم النسخ';
                            btn.style.borderColor = '#28a745';
                            setTimeout(() => {{ btn.innerHTML = 'نسخ النص 📋'; btn.style.borderColor = '#4FA3E3'; }}, 2000);
                        }});
                    }} else {{
                        var el = document.createElement('textarea');
                        el.value = txt;
                        document.body.appendChild(el);
                        el.select();
                        document.execCommand('copy');
                        document.body.removeChild(el);
                        btn.innerHTML = '✅ تم النسخ';
                        btn.style.borderColor = '#28a745';
                        setTimeout(() => {{ btn.innerHTML = 'نسخ النص 📋'; btn.style.borderColor = '#4FA3E3'; }}, 2000);
                    }}
                ">نسخ النص 📋</div>
            </div>
            """
            st.markdown(html_btns, unsafe_allow_html=True)
        
        st.markdown("<hr style='border: 0.5px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)

time.sleep(120)
st.rerun()
