from flask import Flask, render_template, request, jsonify
from typing import Dict, Any, List
import re

app = Flask(__name__, template_folder='templates')

# --- CONFIGURATION MATRIX ---
COEFFICIENTS: Dict[str, float] = {
    "ai_prompt_wh": 3.0,          
    "cloud_compute_wh": 45.0,     
    "data_storage_wh": 0.1,       
    "grid_carbon_intensity": 0.478 
}

def sanitize_string(text: str) -> str:
    """SECURITY: Strips potentially malicious script tags from user inputs."""
    if not text:
        return "Eco Engineer"
    return re.sub(r'[<>&"\']', '', text).strip()

@app.route('/')
def home() -> str:
    """Serves the main application interface."""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate() -> Any:
    """API ENDPOINT: Processes infrastructure metrics and returns optimization data."""
    try:
        data: Dict[str, Any] = request.get_json() or {}
        
        # Parse & Sanitize Input
        name: str = sanitize_string(str(data.get('name', 'Eco Engineer')))
        prompts: float = max(0.0, float(data.get('prompts', 0)))
        hours: float = max(0.0, float(data.get('hours', 0)))
        storage: float = max(0.0, float(data.get('storage', 0)))
        optimization: float = max(0.0, min(100.0, float(data.get('optimization', 0))))
        
        # Core Emissions Mathematics
        total_wh: float = (prompts * COEFFICIENTS["ai_prompt_wh"]) + \
                          (hours * COEFFICIENTS["cloud_compute_wh"]) + \
                          (storage * COEFFICIENTS["data_storage_wh"])
                          
        total_co2_kg: float = (total_wh * COEFFICIENTS["grid_carbon_intensity"]) / 1000
        
        # Mitigation Matrix Logic
        opt_multiplier: float = 1.0 - (optimization / 100.0)
        opt_wh: float = ((prompts * opt_multiplier) * COEFFICIENTS["ai_prompt_wh"]) + \
                        ((hours * opt_multiplier) * COEFFICIENTS["cloud_compute_wh"]) + \
                        (storage * COEFFICIENTS["data_storage_wh"])
                        
        opt_co2_kg: float = (opt_wh * COEFFICIENTS["grid_carbon_intensity"]) / 1000
        saved_co2_kg: float = max(0.0, total_co2_kg - opt_co2_kg)
        
        # Dynamic Heuristic Insights Engine
        insights: List[str] = []
        if total_co2_kg > 0:
            if hours > 10:
                insights.append("⚠️ <b>Cloud Ops:</b> Persistent runtime detected. Recommend implementing automated serverless shutdown protocols during off-peak hours.")
            if prompts > 50:
                insights.append("💡 <b>AI Efficiency:</b> High LLM request load. Consider caching repetitive prompt queries to drop token energy burn.")
            if storage > 1000:
                insights.append("📦 <b>Data Footprint:</b> Massive storage volume. Transition legacy data to cold-storage archives to reduce active server spin.")
            if hours <= 10 and prompts <= 50 and storage <= 1000:
                insights.append("🌱 <b>Optimal State:</b> Architecture is currently running in a highly optimized green state. Excellent work!")
        else:
            insights.append("Awaiting telemetry data to generate architectural recommendations...")

        return jsonify({
            "name": name,
            "energy": round(total_wh, 2),
            "co2": round(total_co2_kg, 4),
            "saved_co2": round(saved_co2_kg, 4),
            "ev_km": round(total_co2_kg * 5.2, 2),
            "insights": insights
        })
        
    except (ValueError, TypeError) as e:
        # Graceful error handling prevents server crashes from bad user data
        return jsonify({"error": "Invalid data format received."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
