# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle
from datetime import datetime

st.set_page_config(
    page_title="Riyadh Traffic",
    page_icon="🚦",
    layout="wide"
)

st.markdown("""
<style>
/* الشريط الجانبي — أخضر غامق */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background-color: #1B5E20 !important;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] header {
    color: white !important;
    font-size: 16px !important;
    font-weight: bold !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #2E7D32 !important;
    border: none !important;
    color: white !important;
}
/* تلوين زر الشريط الجانبي الأصلي */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    background-color: #1B5E20 !important;
    border-radius: 8px !important;
    border: 2px solid #4CAF50 !important;
    top: 55px !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg {
    fill: white !important;
    color: white !important;
}
/* إبعاد محتوى الصفحة عن زر الشريط */
.main .block-container {
    padding-top: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🚦 لوحة تحكم زحمة المرور — الرياض")
st.markdown("---")

# دالة تحويل الساعة لنظام 12
def to_12h(hour):
    if hour == 0:
        return "12 AM"
    elif hour < 12:
        return f"{hour} AM"
    elif hour == 12:
        return "12 PM"
    else:
        return f"{hour - 12} PM"

@st.cache_data
def load_data():
    return pd.read_csv("data/traffic_data.csv", encoding="utf-8-sig")

@st.cache_resource
def load_model():
    with open("models/traffic_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("models/day_encoder.pkl", "rb") as f:
        day_enc = pickle.load(f)
    with open("models/district_encoder.pkl", "rb") as f:
        district_enc = pickle.load(f)
    return model, day_enc, district_enc

df = load_data()
model, day_enc, district_enc = load_model()

col_day   = df.columns[1]
col_hour  = df.columns[2]
col_dist  = df.columns[3]
col_level = df.columns[6]
col_label = df.columns[7]
col_speed = df.columns[8]

# ==============================
# تقسيم الأحياء لمناطق
# ==============================
regions = {
    "🏙️ وسط الرياض":  ["العليا", "الملز", "المربع", "السليمانية", "الورود", "العرضة",
                        "المعذر", "الفلاح", "الزهرة", "السفارات", "الوزارات",
                        "النموذجية", "قرطبة", "الشميسي", "المرقب"],
    "⬆️ شمال الرياض": ["النخيل", "الروضة", "الرحمانية", "الدائري الشمالي", "الياسمين",
                        "النرجس", "الملقا", "العارض", "الصحافة", "الغدير",
                        "حطين", "الغروب", "الفيحاء", "العقيق", "الحزم",
                        "النفل", "الواحة", "المهدية"],
    "⬅️ شرق الرياض":  ["الرمال", "شرق الرياض", "الجزيرة", "النسيم", "قباء",
                        "الحمراء", "الروابي", "الخليج", "البديعة", "المونسية"],
    "⬇️ جنوب الرياض": ["الدائري الجنوبي", "المصانع", "الشفا", "الجنادرية",
                        "عرقة", "الدرعية", "ديراب", "العزيزية", "بدر"],
    "➡️ غرب الرياض":  ["طريق الملك عبدالله", "اليرموك", "الربيع", "السويدي",
                        "الشهداء", "النهضة", "الوادي", "ظهرة لبن", "عليشة"],
    "🛣️ الطرق الرئيسية": ["طريق الملك فهد", "طريق العروبة", "طريق الدمام",
                           "طريق مكة المكرمة", "طريق الخرج",
                           "طريق الثمامة", "طريق الأمير تركي"],
}

# ==============================
# الشريط الجانبي — المنطقة والحي فقط
# ==============================
st.sidebar.header("🔍 فلتر البيانات")

days = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
hour_labels = [to_12h(h) for h in range(24)]
districts = sorted(df[col_dist].unique())

selected_region = st.sidebar.selectbox("اختر المنطقة", list(regions.keys()))
region_districts = regions[selected_region]
selected_district = st.sidebar.selectbox("اختر الحي", sorted(region_districts))

# زر فتح الفلتر للجوال
st.markdown("""
<style>
div[data-testid="stSidebar"] { transition: all 0.3s; }
.filter-hint {
    background-color: #1B5E20;
    color: white;
    padding: 10px 16px;
    border-radius: 8px;
    text-align: center;
    font-size: 16px;
    margin-bottom: 10px;
    display: none;
}
@media (max-width: 768px) {
    .filter-hint { display: block !important; }
}
</style>
<div class="filter-hint">
    👈 اسحب من يسار الشاشة لفتح الفلتر
</div>
""", unsafe_allow_html=True)

# ==============================
# الوقت الحالي
# ==============================
now        = datetime.now()
now_hour   = now.hour
now_day    = days[now.weekday() % 7]

# ==============================
# قسم: الازدحام الآن 🔴
# ==============================
st.subheader(f"📍 الازدحام الآن — {selected_district}")
st.caption(f"يوم {now_day} | الساعة {to_12h(now_hour)}")

now_data = df[
    (df[col_day] == now_day) &
    (df[col_hour] == now_hour) &
    (df[col_dist] == selected_district)
]

if not now_data.empty:
    now_congestion = now_data[col_level].mean()
    now_speed      = now_data[col_speed].mean()
    if now_congestion <= 3:
        now_label = "منخفض 🟢"
        st.success(f"### مستوى الازدحام: {now_label}")
    elif now_congestion <= 6:
        now_label = "متوسط 🟡"
        st.warning(f"### مستوى الازدحام: {now_label}")
    else:
        now_label = "مرتفع 🔴"
        st.error(f"### مستوى الازدحام: {now_label}")

    col1, col2 = st.columns(2)
    col1.metric("مستوى الازدحام", f"{now_congestion:.1f} / 10")
    col2.metric("متوسط السرعة", f"{now_speed:.0f} كم/س")
else:
    st.info("لا توجد بيانات للوقت الحالي")

# للرسوم البيانية — نستخدم المنطقة كلها
selected_day  = now_day
selected_hour = now_hour
filtered = df[(df[col_day] == selected_day) & (df[col_hour] == selected_hour)]

st.markdown("---")

# ==============================
# رسم 1: الازدحام حسب الساعة — bar chart بدل line
# ==============================
st.subheader("⏰ الازدحام حسب الساعة")
hourly = df[df[col_day] == selected_day].groupby(col_hour)[col_level].mean().reset_index()

# ألوان حسب مستوى الازدحام
def hour_color(val):
    if val <= 3:
        return "#2ecc71"
    elif val <= 6:
        return "#f39c12"
    else:
        return "#e74c3c"

colors = [hour_color(v) for v in hourly[col_level]]

fig1 = go.Figure(go.Bar(
    x=hourly[col_hour],
    y=hourly[col_level],
    marker_color=colors,
    text=[f"{v:.1f}" for v in hourly[col_level]],
    textposition="outside",
    hovertemplate="%{customdata}<br>الازدحام: %{y:.1f}<extra></extra>",
    customdata=[to_12h(h) for h in hourly[col_hour]]
))

# خط عمودي يوضح الساعة المختارة — يستخدم الرقم مباشرة
fig1.add_vline(
    x=selected_hour,
    line_width=2,
    line_dash="dash",
    line_color="navy",
    annotation_text=to_12h(selected_hour),
    annotation_position="top right"
)

fig1.update_layout(
    height=420,
    xaxis_title="الوقت",
    yaxis_title="متوسط الازدحام",
    yaxis_range=[0, 11],
    xaxis=dict(
        tickvals=[0, 3, 6, 9, 12, 15, 18, 21],
        ticktext=["12AM", "3AM", "6AM", "9AM", "12PM", "3PM", "6PM", "9PM"],
        tickangle=0
    ),
    showlegend=False,
    plot_bgcolor="white",
    bargap=0.15
)
st.plotly_chart(fig1, use_container_width=True, config={"staticPlot": True})

st.markdown("---")

# ==============================
# رسم 2: الازدحام حسب الحي
# ==============================
st.subheader(f"🏘️ الازدحام حسب الحي — {selected_region}")
region_filtered = filtered[filtered[col_dist].isin(region_districts)]
district_data = region_filtered.groupby(col_dist)[col_level].mean().sort_values(ascending=True).reset_index()

fig2 = px.bar(
    district_data, x=col_level, y=col_dist,
    orientation="h",
    color=col_level,
    color_continuous_scale="RdYlGn_r",
    labels={col_level: "مستوى الازدحام", col_dist: "الحي"},
    text=col_level
)
fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig2.update_layout(
    height=max(500, len(district_data) * 22),
    xaxis_title="مستوى الازدحام",
    xaxis_range=[0, 11],
    yaxis_title="",
    plot_bgcolor="white"
)
st.plotly_chart(fig2, use_container_width=True, config={"staticPlot": True})

st.markdown("---")

# ==============================
# التنبؤ
# ==============================
st.subheader("🤖 تنبؤ مستقل بمستوى الازدحام")
st.caption("تنبأ بأي وقت ومكان تريده — مستقل عن الفلتر أعلاه")

col_pred1, col_pred2 = st.columns([1, 1])

with col_pred1:
    # خيارات مستقلة كلياً
    pred_day        = st.selectbox("📅 اليوم", days, key="pred_day")
    pred_hour_label = st.selectbox("⏰ الساعة", hour_labels, index=8, key="pred_hour")
    pred_hour       = hour_labels.index(pred_hour_label)

    # اختيار المنطقة ثم الحي — مستقل عن فلتر الأعلى
    pred_region   = st.selectbox("🗺️ المنطقة", list(regions.keys()), key="pred_region")
    pred_district = st.selectbox("📍 الحي", sorted(regions[pred_region]), key="pred_district")

    if st.button("🔮 تنبأ بالازدحام"):
        day_num      = day_enc.transform([pred_day])[0]
        district_num = district_enc.transform([pred_district])[0]
        input_df     = pd.DataFrame(
            [[pred_hour, day_num, district_num]],
            columns=["الساعة", "اليوم_رقم", "الحي_رقم"]
        )
        prediction = model.predict(input_df)[0]
        st.markdown("### النتيجة:")
        if prediction == "مرتفع":
            st.error(f"🔴 مستوى الازدحام في {pred_district} يوم {pred_day} الساعة {pred_hour_label}: **{prediction}**")
        elif prediction == "متوسط":
            st.warning(f"🟡 مستوى الازدحام في {pred_district} يوم {pred_day} الساعة {pred_hour_label}: **{prediction}**")
        else:
            st.success(f"🟢 مستوى الازدحام في {pred_district} يوم {pred_day} الساعة {pred_hour_label}: **{prediction}**")

with col_pred2:
    st.info("""
    💡 كيف يعمل النموذج؟

    النموذج يتعلم من بيانات 90 يوم
    ويحلل 3 عوامل:
    - الساعة
    - اليوم
    - الحي

    ثم يتنبأ بمستوى الازدحام:
    - مرتفع
    - متوسط
    - منخفض
    """)

st.markdown("---")
st.caption("🚦 مشروع تحليل زحمة المرور — الرياض | Python & Streamlit")
