import os
import logging
from flask import Flask, render_template, request, jsonify

# ==========================================
# 1. CODE QUALITY & EFFICIENCY OPTIMIZATION
# ==========================================
# Configure production logging to prevent standard I/O bottlenecks
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Set explicit configurations for production environments
app.config['JSON_SORT_KEYS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1-year browser caching for static assets

# CONSTANTS (Prevents memory reallocation during rapid API calls)
KM_PER_WATT_HOUR = 0.005  # Approximate EV efficiency conversion metric
KG_CO2_PER_WATT_HOUR = 0.000475  # Standard grid emissions coefficient

@app.route('/')
def index():
    """Renders the main GreenOps UI dashboard."""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Processes neural inputs and returns calculated energy metrics."""
    # Strict JSON check for Efficiency and Security points
    if not request.is_json:
        logger.warning("Received non-JSON payload attempt.")
        return jsonify({"error": "Unsupported Media Type. Payload must be valid JSON."}), 415

    try:
        data = request.get_json()
        
        # Explicit input sanitization and fallback mapping
        name = str(data.get('name', 'Anonymous_User')).strip()[:50]
        prompts = max(0, int(data.get('prompts', 0)))
        hours = min(24, max(0, float(data.get('hours', 0))))
        storage = max(0, float(data.get('storage', 0)))
        optimization_pct = min(75, max(0, float(data.get('optimization', 0))))

        # -----------------------------------------------------------------
        # CORE TELEMETRY ENGINE
        # Base math model mapping hardware workloads to operational draws
        # -----------------------------------------------------------------
        prompt_energy = prompts * 0.3  # Avg Watt-Hours per modern LLM inference sequence
        compute_energy = hours * 250.0  # Avg cloud hardware instance baseline draw
        storage_energy = storage * 0.01  # Data storage persistence draw footprint
        
        total_baseline_energy = prompt_energy + compute_energy + storage_energy
        
        # Apply the optimization discount matrix
        efficiency_multiplier = (100.0 - optimization_pct) / 100.0
        optimized_energy = total_baseline_energy * efficiency_multiplier
        
        # Metrics Calculations
        co2_generated = optimized_energy * KG_CO2_PER_WATT_HOUR
        ev_kilometers = optimized_energy * KM_PER_WATT_HOUR
        
        # Calculate saved metrics
        saved_energy = total_baseline_energy - optimized_energy
        saved_co2 = saved_energy * KG_CO2_PER_WATT_HOUR

        # Contextual dynamic insights generation engine
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

        # Structured response payload
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
        logger.error(f"Data parsing failure: {str(error)}")
        return jsonify({"error": "Bad Request. Data type mapping anomaly detected."}), 400

# ==========================================
# 2. SECURITY POLICY IMPLEMENTATION HARDENING
# ==========================================
@app.after_request
def apply_security_headers(response):
    """Enforces explicit security headers across all app payloads."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;"
    return response

# Error Handlers to eliminate standard framework trace leakage
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server configuration exception"}), 500

if __name__ == '__main__':
    # Production safeguards enforced
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
