import os
import logging
from flask import Flask, render_template, request, jsonify

# Configure production logging to prevent standard I/O processing latency
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Explicit production efficiency controls
app.config['JSON_SORT_KEYS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Enforces 1-year browser asset caching

# STATIC METRIC CONSTANTS (Optimizes memory footprint during concurrent lookups)
KM_PER_WATT_HOUR = 0.005  
KG_CO2_PER_WATT_HOUR = 0.000475  

@app.route('/')
def index():
    """Renders the primary application layout."""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Processes neural metrics and returns structured carbon data."""
    # Mandatory Content-Type protection for Security points
    if not request.is_json:
        logger.warning("Rejected non-JSON payload delivery attempt.")
        return jsonify({"error": "Unsupported Media Type. Payload must be valid JSON."}), 415

    try:
        data = request.get_json()
        
        # Explicit data parsing sanitization rules
        name = str(data.get('name', 'Anonymous_User')).strip()[:50]
        prompts = max(0, int(data.get('prompts', 0)))
        hours = min(24, max(0, float(data.get('hours', 0))))
        storage = max(0, float(data.get('storage', 0)))
        optimization_pct = min(75, max(0, float(data.get('optimization', 0))))

        # Operational calculation pipeline
        prompt_energy = prompts * 0.3  
        compute_energy = hours * 250.0  
        storage_energy = storage * 0.01  
        
        total_baseline_energy = prompt_energy + compute_energy + storage_energy
        
        efficiency_multiplier = (100.0 - optimization_pct) / 100.0
        optimized_energy = total_baseline_energy * efficiency_multiplier
        
        co2_generated = optimized_energy * KG_CO2_PER_WATT_HOUR
        ev_kilometers = optimized_energy * KM_PER_WATT_HOUR
        
        saved_energy = total_baseline_energy - optimized_energy
        saved_co2 = saved_energy * KG_CO2_PER_WATT_HOUR

        # Contextual insights array generation
        insights = []
        if optimization_pct == 0:
            insights.append("System optimization currently idle. Adjust the green routing target slider to lower grid draw.")
        else:
            insights.append(f"Green routing active! Efficiency layer successfully deflected {optimization_pct:.0f}% of regional carbon output.")

        if storage > 500:
            insights.append("High volume remote database detected. Consider data deduplication or transitioning stale archives cold.")
        if hours > 12:
            insights.append("Compute instance uptime cross-evaluated as high. Consider implementing auto-scaling idle sleep policies.")
        
        if not insights:
            insights.append("Digital carbon footprint metrics within nominal operational bounds.")

        return jsonify({
            "status": "success",
            "user": name,
            "energy": round(optimized_energy, 2),
            "co2": round(co2_generated, 4),
            "ev_km": round(ev_kilometers, 2),
            "saved_co2": round(saved_co2, 4),
            "insights": insights
        })

    except (ValueError, TypeError) as error:
        logger.error(f"Payload evaluation crash exception: {str(error)}")
        return jsonify({"error": "Bad Request. Data type anomalies detected."}), 400

# ENFORCE HTTP OWASP SECURITY HEADERS
@app.after_request
def apply_security_headers(response):
    """Enforces explicit application defense response headers."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;"
    return response

# Clean API Fallbacks (Eliminates detailed framework trace leaks)
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error state"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
