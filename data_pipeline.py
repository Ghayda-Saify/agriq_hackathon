import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
# 1. Crops found in Kaggle relevant to Palestine
KAGGLE_VALID_CROPS = {
    'watermelon': 'Jenin',
    'grapes': 'Hebron',
    'banana': 'Jericho',
    'orange': 'Tulkarm',
    'maize': 'Tubas',  # Equivalent to grains
    'chickpea': 'Nablus',  # Hummus
    'lentil': 'Jenin',
    'mango': 'Qalqilya',
    'apple': 'Hebron'
}

# 2. Critical Palestinian Crops MISSING in Kaggle (We must generate them)
MISSING_CROPS_LOGIC = {
    'Olive': {'district': 'Jenin', 'n': (40, 60), 'p': (20, 40), 'k': (30, 50), 'ph': (6.0, 7.5)},
    'Wheat': {'district': 'Tubas', 'n': (60, 90), 'p': (30, 50), 'k': (30, 50), 'ph': (6.0, 7.0)},
    'Dates': {'district': 'Jericho', 'n': (30, 50), 'p': (10, 30), 'k': (40, 80), 'ph': (7.0, 8.5)},
    'Tomato': {'district': 'Tulkarm', 'n': (80, 120), 'p': (40, 60), 'k': (50, 80), 'ph': (6.0, 6.8)},
    'Cucumber': {'district': 'Jenin', 'n': (70, 100), 'p': (40, 60), 'k': (50, 70), 'ph': (6.0, 7.0)}
}


def generate_soil_data():
    print("🧪 Stage 1: Processing Soil Data...")
    final_soil_data = []

    # --- PART A: LOAD KAGGLE DATA (Real Data) ---
    if os.path.exists('input_files/raw_kaggle_soil.csv'):
        print("   ✅ Found Kaggle dataset. Extracting real samples...")
        df_kaggle = pd.read_csv('input_files/raw_kaggle_soil.csv')

        # Filter only relevant crops
        df_kaggle = df_kaggle[df_kaggle['label'].isin(KAGGLE_VALID_CROPS.keys())].copy()

        for _, row in df_kaggle.iterrows():
            crop_name = row['label'].capitalize()
            # Calculate Yield based on NPK (Scientific Logic)
            # Higher Nitrogen/Rainfall = Better Yield generally
            yield_val = 2.0 + (row['N'] / 200) + (row['rainfall'] / 300) + random.uniform(-0.5, 0.5)

            final_soil_data.append({
                'District': KAGGLE_VALID_CROPS[row['label']],  # Map to Palestine City
                'N': row['N'],
                'P': row['P'],
                'K': row['K'],
                'ph': row['ph'],
                'Crop': crop_name,
                'Yield_Ton': round(yield_val, 2)
            })
    else:
        print("   ⚠️ Warning: 'raw_kaggle_soil.csv' not found! Skipping Kaggle data.")

    # --- PART B: INJECT MISSING PALESTINIAN CROPS (Synthetic) ---
    print("   💉 Injecting missing crops (Olive, Dates, Wheat)...")
    for crop, logic in MISSING_CROPS_LOGIC.items():
        # Generate 150 samples for each missing crop to balance the dataset
        for _ in range(150):
            n = random.uniform(*logic['n'])
            p = random.uniform(*logic['p'])
            k = random.uniform(*logic['k'])
            ph = random.uniform(*logic['ph'])

            # Yield Logic: If N is in upper range, yield is higher
            yield_bonus = 1.0 if n > (logic['n'][0] + logic['n'][1]) / 2 else 0.0
            base_yield = 2.5 + yield_bonus + random.uniform(-0.5, 0.5)

            final_soil_data.append({
                'District': logic['district'],
                'N': round(n, 1),
                'P': round(p, 1),
                'K': round(k, 1),
                'ph': round(ph, 1),
                'Crop': crop,
                'Yield_Ton': round(base_yield, 2)
            })

    # Save Final Soil File
    df_soil = pd.DataFrame(final_soil_data)
    df_soil.to_csv('soil_samples.csv', index=False)
    print(f"   ✅ Done! 'soil_samples.csv' created with {len(df_soil)} records.")
    return df_soil['Crop'].unique()


def generate_market_data(crops_list):
    print("📈 Stage 2: Generating Market History (LSTM Data)...")
    history_data = []
    start_date = datetime(2020, 1, 1)
    weeks = 52 * 4  # 4 Years of weekly data

    for crop in crops_list:
        # Base price config per crop
        base_price = 20 if crop in ['Olive', 'Dates'] else (5 if crop in ['Wheat'] else 10)

        for i in range(weeks):
            current_date = start_date + timedelta(weeks=i)
            month = current_date.month

            # Seasonality (Sine Wave)
            # Summer crops (Melon, Grapes) drop price in months 6-9
            # Winter crops (Citrus) drop price in months 12-2
            season_factor = np.sin((month / 12) * 2 * np.pi)

            # Logic: High Season = High Supply = Low Price
            price_noise = random.uniform(-2, 2)

            if crop in ['Watermelon', 'Grapes', 'Tomato']:
                price = base_price - (season_factor * 3) + price_noise
            elif crop in ['Orange', 'Banana']:
                price = base_price + (season_factor * 3) + price_noise
            else:
                price = base_price + price_noise

            # Ensure price never goes below 1
            price = max(1.5, price)

            # Demand is usually inverse to price, but volatile
            demand = (5000 / price) + random.uniform(-100, 100)

            history_data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Crop': crop,
                'Price': round(price, 2),
                'Demand_Ton': round(demand, 2)
            })

    df_hist = pd.DataFrame(history_data)
    df_hist.to_csv('market_history.csv', index=False)
    print(f"   ✅ Done! 'market_history.csv' created with {len(df_hist)} records.")


if __name__ == "__main__":
    print("🚀 Starting AgriQ Data Pipeline...")
    unique_crops = generate_soil_data()
    generate_market_data(unique_crops)
    print("🎉 All Data Files Ready for Training!")