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

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="موجة نيوز", layout="wide", page_icon="📰")

# --- 2. التصميم الأساسي (CSS) مع حركات الإطار الجديد ---
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

    /* استقامة الهيدر لكلمة حجم الخط */
    .align-font-label {
        display: flex; align-items: center; justify-content: flex-end;
        height: 100%; padding-top: 5px;
    }

    /* تصميم صندوق النص العادي */
    .news-text-box { 
        background-color: #1E1E1E; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid #333;
        margin-bottom: 5px;
    }

    /* 🔥 تصميم الإطار الأصفر النابض للأخبار الجديدة */
    .is-new {
        animation: pulse-border 1.5s infinite;
        border: 2px solid #FFDF00 !important;
    }

    @keyframes pulse-border {
        0% { border-color: #FFDF00; box-shadow: 0 0 5px rgba(255,223,0,0.3); }
        50% { border-color: #ffaa00; box-shadow: 0 0 15px rgba(255,170,0,0.8); }
        100% { border-color: #FFDF00; box-shadow: 0 0 5px rgba(255,223,0,0.3); }
    }

    /* علامة النجمة والجديد */
    .new-badge {
        color: #FFDF00;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 15px;
        background-color: rgba(255, 223, 0, 0.1);
        padding: 5px 15px;
        border-radius: 8px;
        display: inline-block;
        border: 1px solid #FFDF00;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. دالة الصوت وجلب الأخبار ---
def play_notification_sound():
    sound_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    html_str = f'<audio autoplay style="display:none;"><source src="{sound_url}" type="audio/mp3"></audio>'
    components.html(html_str, height=0)

if "seen_links" not in st.session_state: st.session_state.seen_links = set()
if "news_items" not in st.session_state: st.session_state.news_items = []

def fetch_news():
    url = "https://storage.googleapis.com/news-agency/x_world_leaders.xml"
    try:
        feed = feedparser.parse(url)
        new_entries = []
        is_first = len(st.session_state.news_items) == 0
        
        # إعادة تعيين الأخبار القديمة لتصبح غير جديدة
        for item in st.session_state.news_items:
            item['is_new'] = False
            
        for entry in feed.entries[:30]:
            if entry.link not in st.session_state.seen_links:
                pub = entry.get('published_parsed')
                dt_str = ""
                if pub:
                    # توقيت العراق (GMT+3)
                    dt = datetime.fromtimestamp(calendar.timegm(pub), tz=timezone.utc).astimezone(timezone(timedelta(hours=3)))
                    dt_str = dt.strftime('%I:%M %p | %Y/%m/%d')
                
                img = next((l.href for l in entry.get('links', []) if 'image' in l.type), None)
                if not img and 'media_content' in entry: img = entry.media_content[0].get('url')
                
                title = re.sub('<.*?>', '', entry.title).strip()
                desc = re.sub('<.*?>', '', entry.get('description', '')).strip()
                full_text = f"{title}\n\n{desc}"

                new_entries.append({
                    "title": title, "link": entry.link, "desc": desc,
                    "date": dt_str, "img": img, 
                    "id": "".join(filter(str.isalnum, entry.link[-10:])),
                    "copy_text": full_text,
                    "is_new": not is_first # 👈 تحديد الخبر الجديد
                })
                st.session_state.seen_links.add(entry.link)
        
        # إذا تم العثور على أخبار جديدة، قم بتشغيل التنبيه
        if new_entries:
            if not is_first:
                st.toast(f"🔔 تم استلام {len(new_entries)} أخبار جديدة!", icon="🆕")
                play_notification_sound()
            st.session_state.news_items = new_entries + st.session_state.news_items
    except: pass

fetch_news()

# --- 4. الواجهة العلوية (زر حجم الخط مثل Word) ---
col_logo, _, col_label, col_font_box = st.columns([3, 0.5, 0.4, 0.6], vertical_alignment="center")
with col_logo: st.markdown("<h1 style='color: #4FA3E3; margin:0;'>📰 منصة موجة نيوز</h1>", unsafe_allow_html=True)
with col_label: st.markdown("<div class='align-font-label'><p style='font-weight:bold; margin:0; font-size:16px;'>حجم الخط</p></div>", unsafe_allow_html=True)
with col_font_box: f_size = st.selectbox("حجم الخط", options=range(20, 71), index=2, label_visibility="collapsed")

st.success("✅ أهلاً بك في غرفة الأخبار.")

# --- 5. أداة استخراج الصور ---
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
    is_new = item.get('is_new', False)
    
    with st.container():
        col_text, col_img = st.columns([2, 1])
        
        with col_img:
            st.image(img_url, use_container_width=True)
            try:
                img_data = requests.get(img_url).content
                st.download_button(label="📥 تحميل الصورة", data=img_data, file_name="news.jpg", mime="image/jpeg", key=f"dl_{item['id']}", use_container_width=True)
            except: pass
            
        with col_text:
            # تطبيق صندوق الخبر والنبض الأصفر إذا كان جديداً
            box_class = "news-text-box is-new" if is_new else "news-text-box"
            badge_html = "<div class='new-badge'>⭐ عاجل / تغريدة جديدة</div>" if is_new else ""
            
            st.markdown(f"""
            <div class="{box_class}">
                {badge_html}
                <div style='font-size:{f_size}px; font-weight:bold; color:#FFDF00;'>{item['title']}</div>
                <div style='color:#87CEEB; font-size:14px; margin:8px 0;'>{item['date']}</div>
                <p style='font-size:{max(14, f_size-6)}px; color:#ddd; line-height:1.6;'>{item['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # أزرار النسخ والروابط (مستقلة وتعمل 100%)
            safe_text_js = json.dumps(item['copy_text'])
            html_btns = f"""
            <!DOCTYPE html>
            <html dir="rtl">
            <head>
                <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap" rel="stylesheet">
                <style>
                    body {{ margin: 0; padding: 0; font-family: 'Tajawal', sans-serif; background-color: #0E1117; }}
                    .btn-container {{ display: flex; gap: 10px; align-items: center; padding-top: 5px; }}
                    .read-more-btn {{ background-color: #1f77b4; color: white; padding: 8px 15px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 14px; transition: 0.3s; }}
                    .copy-btn {{ background-color: #2d2d2d; color: #4FA3E3; padding: 8px 15px; border: 1px solid #4FA3E3; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 14px; font-family: 'Tajawal', sans-serif; transition: 0.3s; }}
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
                        }} catch(e) {{ alert("فشل النسخ"); }}
                        document.body.removeChild(tempInput);
                    }}
                </script>
            </body>
            </html>
            """
            components.html(html_btns, height=50)
        
        st.markdown("<hr style='border: 0.5px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)

time.sleep(120)
st.rerun()
