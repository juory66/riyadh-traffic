import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import pickle
import os

os.makedirs("models", exist_ok=True)

# ==============================
# تحميل البيانات
# ==============================
df = pd.read_csv("data/traffic_data.csv")
print(f"✅ تم تحميل {len(df):,} سجل")

# ==============================
# تحضير البيانات للنموذج
# ==============================

# تحويل الأيام لأرقام
day_encoder = LabelEncoder()
df["اليوم_رقم"] = day_encoder.fit_transform(df["اليوم"])

# تحويل الأحياء لأرقام
district_encoder = LabelEncoder()
df["الحي_رقم"] = district_encoder.fit_transform(df["الحي"])

# المدخلات (Features)
X = df[["الساعة", "اليوم_رقم", "الحي_رقم"]]

# الهدف (Target)
y = df["تصنيف_الازدحام"]

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n📊 بيانات التدريب: {len(X_train):,}")
print(f"📊 بيانات الاختبار: {len(X_test):,}")

# ==============================
# تدريب النموذج
# ==============================
print("\n⏳ جاري تدريب النموذج...")

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("✅ تم تدريب النموذج!")

# ==============================
# تقييم النموذج
# ==============================
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n🎯 دقة النموذج: {accuracy * 100:.2f}%")
print("\n📋 تقرير التفاصيل:")
print(classification_report(y_test, y_pred))

# ==============================
# حفظ النموذج
# ==============================
with open("models/traffic_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("models/day_encoder.pkl", "wb") as f:
    pickle.dump(day_encoder, f)

with open("models/district_encoder.pkl", "wb") as f:
    pickle.dump(district_encoder, f)

print("✅ تم حفظ النموذج في models/traffic_model.pkl")

# ==============================
# تجربة التنبؤ
# ==============================
print("\n🔮 تجربة التنبؤ:")

test_cases = [
    {"الساعة": 8,  "اليوم": "الأحد",    "الحي": "طريق الملك فهد"},
    {"الساعة": 14, "اليوم": "الجمعة",   "الحي": "الرحمانية"},
    {"الساعة": 17, "اليوم": "الاثنين",  "الحي": "العليا"},
    {"الساعة": 2,  "اليوم": "السبت",    "الحي": "الملز"},
]

for case in test_cases:
    day_num = day_encoder.transform([case["اليوم"]])[0]
    district_num = district_encoder.transform([case["الحي"]])[0]
    pred = model.predict([[case["الساعة"], day_num, district_num]])[0]
    print(f"  ⏰ {case['اليوم']} الساعة {case['الساعة']}:00 | 📍 {case['الحي']} → 🚦 {pred}")