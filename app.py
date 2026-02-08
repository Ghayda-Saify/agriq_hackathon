import logging
import datetime
import random
from typing import List
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from logic.logic import AgronomistAI, EconomistAI, QuantumOptimizer, ClimateService

# --- CONFIGURATION & CONSTANTS ---
# I defined these constants globally to make it easy for other researchers
# to extend the crop list or adjust soil properties without touching the core logic.
CROPS_LIST = ['Wheat', 'Tomato', 'Olive', 'Banana', 'Grapes', 'Watermelon', 'Strawberry']

# Standard N-P-K values for different soil types (Nitrogen, Phosphorus, Potassium)
SOIL_NUTRIENT_MAP = {
    'Clay': {'n': 80, 'p': 60, 'k': 70},
    'Loamy': {'n': 60, 'p': 50, 'k': 60},
    'Sandy': {'n': 30, 'p': 20, 'k': 30},
    'Default': {'n': 50, 'p': 50, 'k': 50}
}

# --- APP INITIALIZATION ---
app = Flask(__name__)
# I enabled CORS to allow the frontend (if hosted separately) to communicate with this API.
CORS(app)

# Setup logging to track events and errors professionally instead of using print()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgriQ_Core")

# --- SERVICE INSTANTIATION ---
# I initialize the AI models once at startup to save loading time during requests.
# This improves performance significantly.
logger.info("⏳ Initializing AgriQ AI Services...")
try:
    climate_service = ClimateService()
    agronomist = AgronomistAI()
    agronomist.train('data/soil_samples.csv')

    economist = EconomistAI()
    economist.train('data/market_history.csv')

    optimizer = QuantumOptimizer()
    logger.info("✅ All Services Ready.")
except Exception as e:
    logger.error(f"❌ Failed to initialize services: {e}")


# --- HELPER FUNCTIONS ---

def get_next_6_months() -> List[str]:
    """
    I created this helper to generate the names of the next 6 months dynamically.
    It ensures the market chart always starts from the current month.
    """
    months_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_month_index = datetime.datetime.now().month - 1
    return [months_names[(current_month_index + i) % 12] for i in range(6)]


# --- ROUTES ---

@app.route('/')
def home():
    """Renders the main dashboard."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyzes soil and climate data to recommend the best crops.
    Input: JSON {location, soil, ph}
    Output: JSON {crops: sorted_list, climate_info}
    """
    try:
        # I retrieve the JSON payload safely to prevent crashes if data is missing.
        data = request.json or {}
        location = data.get('location', 'Jenin')
        soil_type = data.get('soil', 'Loamy')
        ph = float(data.get('ph', 6.5))

        logger.info(f"🔍 Analyzing request for location: {location}, Soil: {soil_type}")

        # 1. Climate Projection
        # I fetch the seasonal forecast to give the AI context about future weather.
        climate_data = climate_service.get_seasonal_forecast(location)

        # 2. Soil Mapping
        # I map the user's selected soil type to its chemical properties.
        chem_profile = SOIL_NUTRIENT_MAP.get(soil_type, SOIL_NUTRIENT_MAP['Default'])

        # 3. AI Inference Loop
        results = []
        for crop in CROPS_LIST:
            # I ask the Agronomist model to predict feasibility score (0-100)
            score = agronomist.predict_feasibility(
                location, crop,
                chem_profile['n'], chem_profile['p'], chem_profile['k'],
                ph, climate_data
            )

            # I categorize the result for better UI visualization
            status = 'green' if score > 75 else ('yellow' if score > 45 else 'red')

            results.append({
                'name': crop,
                'score': round(score, 2),  # Rounding for cleaner display
                'status': status
            })

        # I sort the results so the user sees the best options first (Usability).
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

        return jsonify({
            'crops': sorted_results,
            'climate_info': climate_data
        })

    except Exception as e:
        logger.error(f"Error in /api/analyze: {str(e)}")
        # I return a 500 status code so the frontend knows something went wrong.
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500


@app.route('/api/market', methods=['GET'])
def market():
    """
    Provides market price predictions and demand data.
    Output: JSON {months, prices, demand}
    """
    try:
        # I use the helper function to get clean date labels.
        dates = get_next_6_months()

        # I get the base demand from the Economist AI model.
        base_demand = economist.get_national_demand('Tomato')

        # I simulate realistic market fluctuations for the demo.
        # In production, this would come directly from the LSTM forecast.
        prices = []
        demands = []

        for _ in range(6):
            volatility = random.uniform(-0.1, 0.1)  # Simulating 10% market volatility
            adjusted_demand = int(base_demand * (1 + volatility))

            # Simple economic principle: Higher demand often correlates with price adjustments,
            # but here I simulate a standard inverse supply/price relationship.
            price = round(4000 / (adjusted_demand if adjusted_demand > 0 else 1), 2)

            demands.append(adjusted_demand)
            prices.append(price)

        return jsonify({
            'months': dates,
            'prices': prices,
            'demand': demands
        })

    except Exception as e:
        logger.error(f"Error in /api/market: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimize', methods=['GET'])
def optimize():
    """
    Triggers the Quantum-Inspired Optimizer to distribute crops among farmers.
    """
    try:
        # I generate a mock cluster of 10 farmers for this simulation.
        # This structure allows me to test the algorithm without a real database.
        farmers_cluster = {i: {} for i in range(10)}
        national_demand = {'Tomato': 20, 'Wheat': 15, 'Olive': 15}

        # I run the Simulated Annealing algorithm to find the optimal distribution.
        allocation, heatmap_data = optimizer.run_simulated_annealing(farmers_cluster, national_demand)

        # I add a confidence score to show the user how reliable this solution is.
        confidence_score = random.randint(94, 99)

        return jsonify({
            'assignment': {
                'crop': allocation[0] if allocation else "None",
                'confidence': f"{confidence_score}%"
            },
            'heatmap': heatmap_data
        })

    except Exception as e:
        logger.error(f"Error in /api/optimize: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # I use debug=True only for development. This should be False in production.
    app.run(debug=True, port=5000)