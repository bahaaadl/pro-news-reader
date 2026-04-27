import streamlit as st
import streamlit.components.v1 as components 
import feedparser
import requests
import re
import urllib.parse
import time
import calendar
import json
from datetime import datetime, timezone, timedelta
from deep_translator import GoogleTranslator

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="موجة نيوز", layout="wide", page_icon="📰")

# --- 2. التصميم الأساسي (CSS) ---
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
</style>
""", unsafe_allow_html=True)

# دالة الترجمة السريعة (محفوظة في الذاكرة لتسريع الموقع)
@st.cache_data(show_spinner=False)
def translate_text(text, target_code):
    if not text or target_code == "ar": return text
    try:
        return GoogleTranslator(source='auto', target=target_code).translate(text)
    except:
        return text

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

# --- 4. الواجهة العلوية (تم إضافة سلايدر اللغة هنا) ---
# تقسيم دقيق للأعمدة لتستوعب السلايدر والمربع معاً بشكل أنيق
col_logo, col_lang_lbl, col_lang_slider, col_font_lbl, col_font_box = st.columns([2.5, 0.4, 1.5, 0.5, 0.6], vertical_alignment="center")

with col_logo: 
    st.markdown("<h1 style='color: #4FA3E3; margin:0;'>📰 منصة موجة نيوز</h1>", unsafe_allow_html=True)

with col_lang_lbl:
    # علامة وتسمية اللغة
    st.markdown("<div class='align-font-label'><p style='font-weight:bold; margin:0; font-size:16px;'>🌐 اللغة</p></div>", unsafe_allow_html=True)

with col_lang_slider:
    # سلايدر اللغة الأفقي
    target_lang = st.select_slider(
        "lang_slider", 
        options=["عربي", "English", "كردي"], 
        value="عربي", 
        label_visibility="collapsed"
    )
    # تعيين كود الترجمة (تم استخدام ckb للكردية السورانية لتكون دقيقة ومفهومة)
    lang_map = {"عربي": "ar", "English": "en", "كردي": "ckb"}
    selected_lang_code = lang_map[target_lang]

with col_font_lbl: 
    st.markdown("<div class='align-font-label'><p style='font-weight:bold; margin:0; font-size:16px;'>حجم الخط</p></div>", unsafe_allow_html=True)

with col_font_box: 
    f_size = st.selectbox("حجم الخط", options=range(20, 71), index=2, label_visibility="collapsed")

st.success("✅ أهلاً بك في غرفة الأخبار.")
st.markdown("---")

# --- 5. أداة استخراج الصور 📸 ---
with st.expander("📸 استخراج صورة من منصة X"):
    tweet_url = st.text_input("أدخل رابط التغريدة هنا:")
    if st.button("التقاط الصورة"):
        if tweet_url:
            with st.spinner("جاري الالتقاط... ⏳"):
                api_url = f"https://api.apiflash.com/v1/urltoimage?access_key=85706f41977042d3b642677a65d0d81c&url={urllib.parse.quote(tweet_url)}&element={urllib.parse.quote('article[data-testid=\"tweet\"]')}&delay=5"
                st.image(api_url, caption="تم الالتقاط بنجاح")

st.markdown("---")

# --- 6. عرض الأخبار ---
for item in st.session_state.news_items:
    img_url = item['img'] if item['img'] else "https://via.placeholder.com/350x250?text=Mawja+News"
    
    # === تطبيق الترجمة اللحظية والاتجاه ===
    display_title = translate_text(item['title'], selected_lang_code)
    display_desc = translate_text(item['desc'], selected_lang_code)
    text_dir = "ltr" if selected_lang_code == "en" else "rtl"
    align_txt = "left" if selected_lang_code == "en" else "right"
    
    with st.container():
        col_text, col_img = st.columns([2, 1])
        
        with col_img:
            st.image(img_url, use_container_width=True)
            try:
                img_data = requests.get(img_url).content
                st.download_button(label="📥 تحميل الصورة", data=img_data, file_name="news.jpg", mime="image/jpeg", key=f"dl_{item['id']}", use_container_width=True)
            except: pass
            
        with col_text:
            st.markdown(f"""
            <div dir="{text_dir}" style="text-align: {align_txt};">
                <div style='font-size:{f_size}px; font-weight:bold; color:#FFDF00;'>{display_title}</div>
                <div style='color:#87CEEB; font-size:14px; margin:5px 0;'>{item['date']}</div>
                <p style='font-size:{max(14, f_size-6)}px; color:#ddd;'>{display_desc}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- كود الأزرار السحري (ينسخ النص باللغة المختارة) ---
            translated_full_text = f"{display_title}\n\n{display_desc}"
            safe_text_js = json.dumps(translated_full_text)
            
            html_btns = f"""
            <!DOCTYPE html>
            <html dir="rtl">
            <head>
                <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap" rel="stylesheet">
                <style>
                    body {{ margin: 0; padding: 0; font-family: 'Tajawal', sans-serif; background-color: #1E1E1E; }}
                    .btn-container {{ display: flex; gap: 10px; align-items: center; padding-top: 10px; }}
                    .read-more-btn {{ background-color: #1f77b4; color: white; padding: 8px 15px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 14px; transition: 0.3s; }}
                    .read-more-btn:hover {{ background-color: #155a8a; }}
                    .copy-btn {{ background-color: #2d2d2d; color: #4FA3E3; padding: 8px 15px; border: 1px solid #4FA3E3; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 14px; font-family: 'Tajawal', sans-serif; transition: 0.3s; }}
                    .copy-btn:hover {{ background-color: #4FA3E3; color: white; }}
                </style>
            </head>
            <body>
                <div class="btn-container">
                    <a href="{item['link']}" target="_blank" class="read-more-btn">فتح الرابط 🔗</a>
                    <button class="copy-btn" onclick="copyToClipboard(this)">نسخ النص 📋</button>
                </div>
                <script>
                    function copyToClipboard(btn) {{
                        const text = {safe_text_js};
                        const tempInput = document.createElement("textarea");
                        tempInput.value = text;
                        document.body.appendChild(tempInput);
                        tempInput.select();
                        try {{
                            document.execCommand("copy");
                            const oldText = btn.innerHTML;
                            btn.innerHTML = "✅ تم النسخ بنجاح";
                            btn.style.backgroundColor = "#28a745";
                            btn.style.borderColor = "#28a745";
                            btn.style.color = "white";
                            setTimeout(() => {{
                                btn.innerHTML = oldText;
                                btn.style.backgroundColor = "#2d2d2d";
                                btn.style.borderColor = "#4FA3E3";
                                btn.style.color = "#4FA3E3";
                            }}, 2000);
                        }} catch(e) {{
                            alert("فشل النسخ");
                        }}
                        document.body.removeChild(tempInput);
                    }}
                </script>
            </body>
            </html>
            """
            components.html(html_btns, height=60)
        
        st.markdown("<hr style='border: 0.5px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)

time.sleep(120)
st.rerun()
