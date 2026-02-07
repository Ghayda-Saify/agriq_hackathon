import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 1. إعدادات المحاصيل الفلسطينية
PALESTINE_CROPS = {
    'rice': 'Jericho',  # يحتاج حرارة وماء (تجريبي)
    'maize': 'Jenin',  # جنين مشهورة بالحبوب
    'chickpea': 'Hebron',  # الحمص
    'kidneybeans': 'Tubas',
    'pigeonpeas': 'Salfit',
    'mothbeans': 'Nablus',
    'mungbean': 'Tulkarm',
    'blackgram': 'Jenin',
    'lentil': 'Nablus',  # العدس
    'pomegranate': 'Hebron',  # الرمان
    'banana': 'Jericho',  # الموز (أريحا حصراً)
    'mango': 'Qalqilya',  # المانجا (قلقيلية)
    'grapes': 'Hebron',  # العنب (الخليل)
    'watermelon': 'Jenin',  # البطيخ (جنين)
    'muskmelon': 'Jenin',  # الشمام
    'apple': 'Hebron',  # التفاح
    'orange': 'Tulkarm',  # الحمضيات
    'papaya': 'Jericho',
    'cotton': 'Jenin'  # القطن
}


def process_data():
    print("🔄 Loading Kaggle Data...")
    try:
        # قراءة ملف كاغل الأصلي
        df = pd.read_csv('raw_kaggle_soil.csv')

        # 1. فلترة المحاصيل (نأخذ فقط ما يزرع في فلسطين)
        df = df[df['label'].isin(PALESTINE_CROPS.keys())].copy()

        # 2. تحسين البيانات (Capitalize)
        df['Crop'] = df['label'].str.capitalize()

        # 3. إضافة المدن (Logic Injection)
        # نستخدم القاموس أعلاه لتحديد المدينة الأنسب
        df['District'] = df['label'].map(PALESTINE_CROPS)

        # 4. حساب الإنتاجية المتوقعة (Yield) بناءً على علم التربة
        # المعادلة: إذا كانت التربة غنية (N عالي) والماء جيد = إنتاج عالي
        def calculate_yield(row):
            base_yield = 3.0
            if row['N'] > 80: base_yield += 1.0
            if row['P'] > 50: base_yield += 0.5
            if row['rainfall'] > 100: base_yield += 0.5
            return round(base_yield + random.uniform(-0.5, 0.5), 2)

        df['Yield'] = df.apply(calculate_yield, axis=1)

        # 5. حفظ ملف التربة (للمرحلة 1 - Random Forest)
        # نختار الأعمدة التي يحتاجها تطبيقنا بالضبط
        soil_df = df[['District', 'Crop', 'N', 'P', 'K', 'ph', 'Yield']]
        soil_df.to_csv('soil_samples.csv', index=False)
        print(f"✅ Created 'soil_samples.csv' from Kaggle ({len(soil_df)} rows).")

        # ---------------------------------------------------------

        # 6. توليد تاريخ السوق (للمرحلة 2 - LSTM)
        # بما أن كاغل لا يحتوي على أسعار تاريخية، سنقوم بتوليدها بناءً على المحاصيل الموجودة
        print("📈 Generating Market History based on Kaggle Crops...")

        market_data = []
        unique_crops = df['Crop'].unique()
        start_date = datetime(2020, 1, 1)
        days = 365 * 5  # 5 سنوات

        for crop in unique_crops:
            # سعر أساسي مختلف لكل محصول
            base_price = random.uniform(2000, 5000)

            for day in range(0, days, 7):  # بيانات أسبوعية
                curr_date = start_date + timedelta(days=day)
                month = curr_date.month

                # معادلة الموسمية (Sine Wave)
                seasonality = np.sin((month / 12) * 2 * np.pi)

                # السعر يتأثر بالموسم والعشوائية
                price = base_price + (seasonality * 500) + random.uniform(-200, 200)

                # الطلب عكس السعر
                demand = (10000000 / price) + random.uniform(-100, 100)

                market_data.append([
                    curr_date.strftime('%Y-%m-%d'),
                    crop,
                    round(price, 2),
                    round(int(demand), 0)
                ])

        market_df = pd.DataFrame(market_data, columns=['Date', 'Crop', 'Price_NIS_Ton', 'Demand_Ton'])
        market_df.to_csv('market_history.csv', index=False)
        print(f"✅ Created 'market_history.csv' ({len(market_df)} rows).")

    except FileNotFoundError:
        print("❌ Error: 'raw_kaggle_soil.csv' not found. Download it from Kaggle Crop Recommendation Dataset.")


if __name__ == "__main__":
    process_data()