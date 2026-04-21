import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone, timedelta
import calendar
import re
import html
import time
from streamlit_cookies_manager import EncryptedCookieManager
import uuid
import urllib.parse
import json
import os
from datetime import date

# --- إعداد الكوكيز (كلمة سر التشفير) ---
cookies = EncryptedCookieManager(password="L6V299S8B1N0M3X4Z5Q6W7E8")
if not cookies.ready():
    st.stop()

# إنشاء أو قراءة رقم تعريفي ثابت للجهاز (لمنع مشكلة الريفرش)
device_id = cookies.get("device_id")
if not device_id:
    device_id = str(uuid.uuid4())
    cookies["device_id"] = device_id
    cookies.save()

# --- إعدادات الصفحة ---
st.set_page_config(page_title="قارئ الأخبار الاحترافي", layout="wide", page_icon="📰")

# --- CSS لإخفاء شريط الإعدادات وتحسين التصميم ---
import streamlit as st
# (استدعاء باقي مكتباتك هنا مثل pandas أو requests)

# 1. كود التصميم وإخفاء القوائم (الكود الذي أرسلته لي الآن)
st.markdown("""
<style>
/* إخفاء قوائم ستريمليت والشريط الأبيض */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stAppDeployButton {display:none;}
[data-testid="stStatusWidget"] {display:none;}

/* إعدادات الخط */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; }

/* 💻 تصميم البطاقات الأساسي (لشاشات الكمبيوتر) */
.news-card { 
    display: flex; 
    flex-direction: row; 
    direction: rtl; 
    background-color: #1E1E1E; 
    border-radius: 12px; 
    padding: 20px; 
    margin-bottom: 20px; 
    border: 2px solid #444444; 
}
.news-card.new-item { animation: pulse-border 2s infinite; }
@keyframes pulse-border { 0% { border-color: #FFDF00; } 50% { border-color: #B8860B; } 100% { border-color: #FFDF00; } }
.news-content { flex: 1; padding-left: 20px; text-align: right; }
.news-image-container { width: 250px; height: 250px; flex-shrink: 0; border-radius: 10px; overflow: hidden; border: 1px solid #333; }
.news-image-container img { width: 100%; height: 100%; object-fit: cover; }
.read-more-btn { background-color: #1f77b4; color: white !important; padding: 8px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; display: inline-block; }

/* 📱 التوافق التلقائي مع شاشات الموبايل (التعديل السحري) */
@media (max-width: 768px) {
    .news-card {
        flex-direction: column; 
        padding: 15px;
    }
    .news-content {
        padding-left: 0; 
        margin-bottom: 15px; 
    }
    .news-image-container {
        width: 100%; 
        height: auto;
        min-height: 200px;
        max-height: 300px;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. كود جلب الأخبار وعرضها
# ==========================================
st.title("📰 منصة موجة نيوز")

# (ضع هنا الكود الخاص بك الذي يقوم بجلب الأخبار من RSS أو تويتر وعرضها داخل كلاس .news-card)

def play_notification_sound():
    sound_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    html_str = f'<audio autoplay style="display:none;"><source src="{sound_url}" type="audio/mp3"></audio>'
    st.components.v1.html(html_str, height=0)

# --- نظام تسجيل الدخول المتعدد ---
@st.cache_resource
def get_active_sessions():
    return {}

active_sessions = get_active_sessions()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = cookies.get("is_logged_in") == "true"
if "current_username" not in st.session_state:
    st.session_state.current_username = cookies.get("current_username")

if st.session_state.logged_in and st.session_state.current_username:
    u = st.session_state.current_username
    if active_sessions.get(u) != device_id:
        st.session_state.logged_in = False
        cookies["is_logged_in"] = "false"
        cookies["current_username"] = ""
        cookies.save()

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔒 دخول النظام</h1>", unsafe_allow_html=True)
    
    valid_users = {
        "mwj1": "@@@", "mwj2": "@@@", "mwj3": "@@@", "mwj4": "@@@", "mwj5": "@@@"
    }
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        
        force_login = False
        if u in active_sessions and active_sessions[u] != device_id:
            st.warning(f"⚠️ الحساب '{u}' مستخدم حالياً من جهاز آخر.")
            force_login = st.checkbox("إنهاء الجلسة الأخرى والدخول إجبارياً")
            
        if st.button("دخول", use_container_width=True):
            if u in valid_users and valid_users[u] == p:
                if u in active_sessions and active_sessions[u] != device_id and not force_login:
                    st.error("❌ لا يمكنك الدخول. الرجاء تحديد مربع 'إنهاء الجلسة الأخرى' لطرد الجهاز القديم.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.current_username = u
                    active_sessions[u] = device_id 
                    
                    cookies["is_logged_in"] = "true"
                    cookies["current_username"] = u
                    cookies.save()
                    st.rerun()
            else: 
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
    st.stop()

# --- جلب الأخبار ---
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
            if not is_first:
                st.toast(f"🔔 تم استلام {len(new_entries)} أخبار جديدة!", icon="🆕")
                play_notification_sound()
            st.session_state.news_items = new_entries + st.session_state.news_items
    except: pass

fetch_news()

# --- شريط الإعدادات العلوي ---
col_logout, col_space, col_slider = st.columns([1, 2, 2])
with col_logout:
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        u = st.session_state.current_username
        if u in active_sessions and active_sessions[u] == device_id:
            del active_sessions[u]
            
        cookies["is_logged_in"] = "false"
        cookies["current_username"] = ""
        cookies.save()
        st.session_state.logged_in = False
        st.rerun()

with col_slider:
    st.markdown("<div style='text-align: right; color: white; margin-bottom: -20px; font-weight: bold;'>حجم الخط:</div>", unsafe_allow_html=True)
    f_size = st.slider("", 15, 50, 22, label_visibility="collapsed")

st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px; border-color: #444;'>", unsafe_allow_html=True)

# ==========================================
# --- أداة التقاط التغريدات (مع نظام العداد المنفصل لكل مستخدم) ---
# ==========================================
STATS_FILE = "user_usage.json"
LIMIT = 50

def load_usage():
    """تحميل البيانات وتصفيرها تلقائياً في اليوم الجديد"""
    today = str(date.today())
    default_data = {"last_date": today, "users": {}}
    
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
                # إذا دخلنا في يوم جديد، نرجع العدادات صفر
                if data.get("last_date") != today:
                    return default_data
                # حماية: إذا كان الملف القديم لا يحتوي على "users"
                if "users" not in data:
                    return default_data
                return data
        except:
            return default_data
    return default_data

def get_user_count(data, username):
    """جلب عدد الصور المسحوبة للمستخدم الحالي فقط"""
    return data["users"].get(username, 0)

def increment_usage(username):
    """زيادة العداد وحفظه باسم المستخدم الحالي فقط"""
    data = load_usage()
    current_count = get_user_count(data, username)
    
    # تحديث رقم المستخدم
    data["users"][username] = current_count + 1
    data["last_date"] = str(date.today())
    
    with open(STATS_FILE, "w") as f:
        json.dump(data, f)

if "snapshot_img" not in st.session_state:
    st.session_state.snapshot_img = None

st.subheader("📸 استخراج صورة")

# جلب اسم المستخدم الحالي من الجلسة
current_user = st.session_state.current_username

# جلب بيانات الاستخدام وحساب المتبقي لهذا المستخدم تحديداً
usage_data = load_usage()
user_count = get_user_count(usage_data, current_user)
remaining = LIMIT - user_count

# التحقق من الحد قبل السماح بالالتقاط
if user_count >= LIMIT:
    st.error(f"⚠️ عذراً {current_user}، لقد تجاوزت الحد المسموح لك ({LIMIT} صورة يومياً). سيتم تصفير عدادك غداً.")
else:
    APIFLASH_KEY = "85706f41977042d3b642677a65d0d81c" 

    with st.expander(f"اضغط هنا لفتح أداة الالتقاط (المتبقي لك اليوم: {remaining})", expanded=False):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            tweet_url = st.text_input("رابط التغريدة", placeholder="https://x.com/...", label_visibility="collapsed")
        with col_btn:
            capture_btn = st.button("التقط الصورة", use_container_width=True)
            
        if capture_btn and tweet_url:
            with st.spinner("جاري فتح التغريدة وتطبيق إعدادات ApiFlash القياسية... ⏳"):
                try:
                    encoded_url = urllib.parse.quote(tweet_url)
                    
                    # 1. إخفاء البنرات
                    elements_to_hide = "#layers, [data-testid='bottom-banner']"
                    encoded_hide = urllib.parse.quote(elements_to_hide)
                    
                    # 2. كود فتح النص الطويل
                    js_click = """
                    setTimeout(() => {
                        const els = document.querySelectorAll('span, div');
                        for (let e of els) {
                            if (e.innerText && (e.innerText.includes('عرض المزيد') || e.innerText.includes('Show more'))) {
                                e.click();
                                break;
                            }
                        }
                    }, 1000);
                    """
                    encoded_js = urllib.parse.quote(js_click)
                    
                    # 3. تحديد مربع التغريدة
                    encoded_element = urllib.parse.quote('article[data-testid="tweet"]')
                    
                    # 4. الرابط السحري
                    api_url = f"https://api.apiflash.com/v1/urltoimage?access_key={APIFLASH_KEY}&url={encoded_url}&format=png&width=1024&scale_factor=2&delay=5&scroll_page=true&hide_elements={encoded_hide}&js={encoded_js}&element={encoded_element}&response_type=image"
                    
                    resp = requests.get(api_url)
                    if resp.status_code == 200:
                        st.session_state.snapshot_img = resp.content
                        
                        # ✅ زيادة العداد لهذا المستخدم فقط
                        increment_usage(current_user) 
                        st.rerun() 
                    else:
                        st.error(f"❌ فشل الالتقاط. كود الخطأ: {resp.status_code}")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
                    
        if st.session_state.snapshot_img:
            st.success("✅ تم الالتقاط بنجاح (تصميم عريض بدون مساحات ميتة)!")
            st.image(st.session_state.snapshot_img, use_container_width=True)
            
            col_down, col_close = st.columns(2)
            with col_down:
                st.download_button(
                    label="💾 تحميل لقطة الشاشة",
                    data=st.session_state.snapshot_img,
                    file_name=f"tweet_hq_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True
                )
            with col_close:
                if st.button("❌ إغلاق الصورة", use_container_width=True):
                    st.session_state.snapshot_img = None
                    st.rerun()

st.markdown("<hr style='margin-bottom: 20px; border-color: #444;'>", unsafe_allow_html=True)
# ==========================================

# --- عرض الأخبار ---
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
