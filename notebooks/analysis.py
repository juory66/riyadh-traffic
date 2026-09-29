import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# إعداد الخط والستايل
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12
sns.set_theme(style="whitegrid")

# إنشاء مجلد للرسوم
os.makedirs("notebooks/charts", exist_ok=True)

# ==============================
# تحميل البيانات
# ==============================
df = pd.read_csv("data/traffic_data.csv")
print(f"✅ تم تحميل {len(df):,} سجل")
print(df.head())

# ==============================
# رسم 1: متوسط الازدحام حسب الساعة
# ==============================
hourly = df.groupby("الساعة")["مستوى_الازدحام"].mean().reset_index()

plt.figure()
sns.lineplot(data=hourly, x="الساعة", y="مستوى_الازدحام", color="tomato", linewidth=2.5, marker="o")
plt.title("متوسط الازدحام حسب الساعة", fontsize=16)
plt.xlabel("الساعة")
plt.ylabel("مستوى الازدحام")
plt.xticks(range(0, 24))
plt.tight_layout()
plt.savefig("notebooks/charts/01_hourly_congestion.png")
plt.show()
print("✅ رسم 1 تم")

# ==============================
# رسم 2: متوسط الازدحام حسب اليوم
# ==============================
day_order = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
daily = df.groupby("اليوم")["مستوى_الازدحام"].mean().reindex(day_order).reset_index()

plt.figure()
sns.barplot(data=daily, x="اليوم", y="مستوى_الازدحام", palette="Reds_r")
plt.title("متوسط الازدحام حسب اليوم", fontsize=16)
plt.xlabel("اليوم")
plt.ylabel("مستوى الازدحام")
plt.tight_layout()
plt.savefig("notebooks/charts/02_daily_congestion.png")
plt.show()
print("✅ رسم 2 تم")

# ==============================
# رسم 3: متوسط الازدحام حسب الحي
# ==============================
district = df.groupby("الحي")["مستوى_الازدحام"].mean().sort_values(ascending=False).reset_index()

plt.figure(figsize=(14, 6))
sns.barplot(data=district, x="الحي", y="مستوى_الازدحام", palette="OrRd_r")
plt.title("متوسط الازدحام حسب الحي", fontsize=16)
plt.xlabel("الحي")
plt.ylabel("مستوى الازدحام")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("notebooks/charts/03_district_congestion.png")
plt.show()
print("✅ رسم 3 تم")

# ==============================
# رسم 4: توزيع تصنيفات الازدحام
# ==============================
labels = df["تصنيف_الازدحام"].value_counts()

plt.figure(figsize=(7, 7))
plt.pie(labels, labels=labels.index, autopct="%1.1f%%",
        colors=["#2ecc71", "#f39c12", "#e74c3c"], startangle=140)
plt.title("توزيع تصنيفات الازدحام", fontsize=16)
plt.tight_layout()
plt.savefig("notebooks/charts/04_congestion_distribution.png")
plt.show()
print("✅ رسم 4 تم")

# ==============================
# رسم 5: Heatmap الساعة × اليوم
# ==============================
heatmap_data = df.groupby(["اليوم", "الساعة"])["مستوى_الازدحام"].mean().unstack()
heatmap_data = heatmap_data.reindex(day_order)

plt.figure(figsize=(16, 6))
sns.heatmap(heatmap_data, cmap="YlOrRd", linewidths=0.5, annot=False)
plt.title("خريطة الازدحام — اليوم vs الساعة", fontsize=16)
plt.xlabel("الساعة")
plt.ylabel("اليوم")
plt.tight_layout()
plt.savefig("notebooks/charts/05_heatmap.png")
plt.show()
print("✅ رسم 5 تم")

print("\n🎉 تم حفظ جميع الرسوم في مجلد notebooks/charts/")