# 🌱 AgriQ | Intelligent Farming Engine

![AgriQ Banner](static/img/banner_placeholder.png) 
> **"From Chaos to Calculation."** > A Quantum-Inspired Agricultural Planning System designed to optimize crop distribution, predict market trends, and ensure national food security.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-green)
![AI](https://img.shields.io/badge/AI-RandomForest%20%7C%20LSTM-orange)
![Quantum](https://img.shields.io/badge/Algorithm-Quantum--Inspired-purple)

---

## 📖 Overview

**AgriQ** is a decision-support system built to solve the "Agricultural Chaos" problem in Palestine (and similar markets), where random farming leads to market saturation and price crashes.

Instead of traditional farming, AgriQ uses a **3-Stage Hybrid Intelligence Pipeline** to answer:
1.  **Can** I grow this? (Bio-Feasibility)
2.  **Should** I grow this? (Economic Viability)
3.  **How much** should we all grow? (National Equilibrium)

---

## 🏗️ Architecture: The 3-Stage Pipeline

AgriQ operates on three integrated logic layers:

### 1. The Agronomist (Bio-Feasibility) 🧬
* **Algorithm:** Random Forest Regressor.
* **Input:** Soil samples (NPK, pH), location, and historical climate data.
* **Output:** A feasibility score (0-100%) for specific crops.
* **Logic:** Analyzes soil chemistry and projected weather to ensure biological success.

### 2. The Economist (Market Intelligence) 📈
* **Algorithm:** LSTM (Long Short-Term Memory) Neural Networks.
* **Input:** 10 years of historical price and demand data (Source: PCBS).
* **Output:** 6-month forecast for price and demand.
* **Logic:** Detects seasonal trends and predicts market crashes before they happen.

### 3. The Quantum Planner (National Distribution) ⚛️
* **Algorithm:** Simulated Annealing (Quantum-Inspired Optimization).
* **Input:** Aggregated farmer data + National Demand Forecast.
* **Output:** Optimal crop allocation map.
* **Logic:** Minimizes the "Energy Function" (Supply - Demand gap) to reach a state of National Equilibrium.

---

## 🚀 Project Structure

```bash
AgriQ/
│
├── data/                    # CSV Datasets (Soil, Market History)
│   ├── soil_samples.csv
│   └── market_history.csv
│
├── logic/                   # Core AI Algorithms (The "Brain")
│   ├── climate_service.py
│   └── logic.py             # Contains AgronomistAI, EconomistAI, QuantumOptimizer
│
├── static/                  # Frontend Assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── img/
│       └── map_bg.png       # Map overlay image
│
├── templates/               # HTML Views
│   └── index.html
│
├── app.py                   # Flask Server (The "Glue")
├── data_pipline.py                   # Flask Server (The "Glue")
└── README.md                # Documentation
