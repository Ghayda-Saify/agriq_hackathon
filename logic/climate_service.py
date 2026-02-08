import random
import datetime
from typing import Dict, Any


class ClimateService:
    """
    Service responsible for retrieving climate data.
    In a production environment, this would connect to an external API (e.g., OpenWeatherMap, NASA Power).
    For this MVP, I simulate historical climate patterns specific to Palestinian districts.
    """

    def __init__(self):
        # I defined the base climate profiles for major Palestinian districts.
        # This acts as my "Ground Truth" database.
        # Temp is in Celsius, Rainfall in mm (annual average context).
        self.climate_profiles = {
            'Jenin': {'base_temp': 25, 'rain_factor': 1.2, 'type': 'Mediterranean'},
            'Jericho': {'base_temp': 32, 'rain_factor': 0.2, 'type': 'Arid'},
            'Hebron': {'base_temp': 18, 'rain_factor': 1.1, 'type': 'Highland'},
            'Nablus': {'base_temp': 22, 'rain_factor': 1.3, 'type': 'Mediterranean'},
            'Tulkarm': {'base_temp': 24, 'rain_factor': 1.4, 'type': 'Coastal Plain'},
            'Gaza': {'base_temp': 26, 'rain_factor': 0.9, 'type': 'Coastal'},
            'Ramallah': {'base_temp': 20, 'rain_factor': 1.2, 'type': 'Highland'}
        }

    def get_seasonal_forecast(self, location: str) -> Dict[str, Any]:
        """
        Generates a 3-month climate projection based on the current date and location.
        Crucial for the Agronomist AI to decide if a crop can survive the next season.
        """

        # I sanitize the input to ensure we match the key even if casing differs.
        city = location.capitalize()
        profile = self.climate_profiles.get(city, self.climate_profiles['Jenin'])

        # Determine the current season dynamically
        current_month = datetime.datetime.now().month
        season_name, temp_mod, rain_mod = self._get_season_modifiers(current_month)

        # I calculate the projected metrics by applying seasonal modifiers to the base profile.
        # Example: Jericho (32) + Winter (-10) = 22C.
        projected_temp = profile['base_temp'] + temp_mod

        # Rainfall calculation: Base factor * Season wetness * Random variation
        projected_rain = profile['rain_factor'] * rain_mod * random.uniform(0.8, 1.2) * 50

        # I construct a structured response for the AI engine.
        return {
            'location': city,
            'season_name': season_name,
            'avg_temp_c': round(projected_temp, 1),
            'rainfall_mm': round(projected_rain, 1),
            'climate_type': profile['type'],
            'risk_factor': self._calculate_risk(projected_temp, projected_rain, profile['type'])
        }

    def _get_season_modifiers(self, month: int):
        """
        Helper method to return seasonal adjustments.
        Returns: (Season Name, Temp Modifier, Rain Modifier)
        """
        if month in [12, 1, 2]:
            return 'Winter', -8.0, 2.0  # Cold, Wet
        elif month in [3, 4, 5]:
            return 'Spring', 0.0, 0.8  # Moderate
        elif month in [6, 7, 8]:
            return 'Summer', 8.0, 0.0  # Hot, Dry
        else:
            return 'Autumn', -2.0, 0.5  # Cooling down

    def _calculate_risk(self, temp: float, rain: float, c_type: str) -> str:
        """
        Internal logic to flag extreme weather events (Heatwaves, Frost).
        """
        if temp > 38:
            return "High Heat Stress"
        if temp < 5:
            return "Frost Warning"
        if c_type == 'Arid' and rain > 100:
            return "Flash Flood Risk"  # Rare but possible in Jericho
        return "Stable"


# --- UNIT TEST ---
if __name__ == "__main__":
    # I added this block to test the service independently before integrating it.
    service = ClimateService()
    print(service.get_seasonal_forecast("Jericho"))
    print(service.get_seasonal_forecast("Hebron"))