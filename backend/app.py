import os
from flask import Flask, request, jsonify, send_from_directory
import database
import preprocess

# Absolute paths for clean frontend / backend separation
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
PUBLIC_DIR = os.path.join(FRONTEND_DIR, 'public')

app = Flask(__name__, static_folder=PUBLIC_DIR)

# Initialize database on startup
database.init_db()

# ========================================================
# FRONTEND ROUTING
# ========================================================

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/dashboard')
@app.route('/sem7_dashboard.html')
def dashboard():
    return send_from_directory(FRONTEND_DIR, 'sem7_dashboard.html')

@app.route('/public/<path:asset_path>')
def serve_public_assets(asset_path):
    return send_from_directory(PUBLIC_DIR, asset_path)


# ========================================================
# TRACKING API ENDPOINTS (Semester VII Core Deliverable)
# ========================================================

@app.route('/api/track/init', methods=['POST'])
def track_init():
    """Initializes or updates visitor profile."""
    data = request.get_json() or {}
    visitor_id = data.get('visitor_id')
    device_type = data.get('device_type', 'Desktop')
    browser = data.get('browser', 'Chrome')
    os_name = data.get('os', 'Windows')
    screen_res = data.get('screen_resolution', '1920x1080')

    if not visitor_id:
        return jsonify({'error': 'visitor_id is required'}), 400

    database.register_user(visitor_id, device_type, browser, os_name, screen_res)
    return jsonify({'status': 'success', 'message': 'Visitor initialized'})

@app.route('/api/track/pageview', methods=['POST'])
def track_pageview():
    """Records page visit event with session association."""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    visitor_id = data.get('visitor_id')
    page_url = data.get('page_url', '/')
    page_title = data.get('page_title', '')
    referrer = data.get('referrer', '')
    dwell_time = float(data.get('dwell_time', 0))
    scroll_depth = float(data.get('scroll_depth', 0))

    if not session_id or not visitor_id:
        return jsonify({'error': 'session_id and visitor_id required'}), 400

    database.record_page_view(session_id, visitor_id, page_url, page_title, referrer, dwell_time, scroll_depth)
    return jsonify({'status': 'success', 'message': 'Pageview logged'})

@app.route('/api/track/click', methods=['POST'])
def track_click():
    """Records interactive click events."""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    visitor_id = data.get('visitor_id')
    page_url = data.get('page_url', '/')
    element_id = data.get('element_id', '')
    element_tag = data.get('element_tag', '')
    element_class = data.get('element_class', '')
    element_text = data.get('element_text', '')
    x_pos = float(data.get('x_pos', 0))
    y_pos = float(data.get('y_pos', 0))

    if not session_id or not visitor_id:
        return jsonify({'error': 'session_id and visitor_id required'}), 400

    database.record_click_event(session_id, visitor_id, page_url, element_id, element_tag, element_class, element_text, x_pos, y_pos)
    return jsonify({'status': 'success', 'message': 'Click logged'})

@app.route('/api/track/heartbeat', methods=['POST'])
def track_heartbeat():
    """Updates session duration periodically."""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    duration = float(data.get('duration_seconds', 0))

    if session_id:
        database.update_session_heartbeat(session_id, duration)
    return jsonify({'status': 'success'})

@app.route('/api/track/product', methods=['POST'])
def track_product():
    """Records specific product interaction events (views, cart adds, purchases, detail clicks)."""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    visitor_id = data.get('visitor_id')
    product_id = data.get('product_id', 'unknown_prod')
    product_name = data.get('product_name', 'Unknown Product')
    category = data.get('category', 'General')
    price = float(data.get('price', 0))
    event_type = data.get('event_type', 'view')
    dwell_time = float(data.get('dwell_time', 0))

    if not session_id or not visitor_id:
        return jsonify({'error': 'session_id and visitor_id required'}), 400

    database.record_product_event(session_id, visitor_id, product_id, product_name, category, price, event_type, dwell_time)
    return jsonify({'status': 'success', 'message': f'Product event {event_type} recorded'})

@app.route('/api/metrics/products', methods=['GET'])
def get_product_metrics_endpoint():
    """Returns aggregated per-product tracking metrics and category distribution."""
    metrics = database.get_product_metrics()
    return jsonify(metrics)

# ========================================================
# ANALYTICS & PREPROCESSING APIS (Semester VII Deliverable)
# ========================================================

@app.route('/api/metrics/summary', methods=['GET'])
def get_metrics_summary():
    """Returns real-time aggregated metrics from database."""
    summary = database.get_realtime_metrics()
    return jsonify(summary)

@app.route('/api/metrics/processed', methods=['GET'])
def get_processed_data():
    """Runs data preprocessing pipeline and returns behavioral features."""
    try:
        df, stats = preprocess.preprocess_and_engineer_features()
        if df is None:
            return jsonify({'status': 'empty', 'message': 'No session data to process'})
        # Return top 25 recent sessions with engineered features
        records = df.head(25).to_dict(orient='records')
        return jsonify({
            'status': 'success',
            'summary': stats,
            'samples': records
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/seed', methods=['POST'])
def trigger_seed():
    """Allows seeding realistic test data directly from UI."""
    try:
        from seed_data import seed_database
        seed_database(num_visitors=20)
        return jsonify({'status': 'success', 'message': 'Database seeded successfully with 20 realistic visitor journeys!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/<path:page_name>')
def serve_page(page_name):
    # Check if requested file exists in frontend root (e.g. products.html, blog.html)
    full_path = os.path.join(FRONTEND_DIR, page_name)
    if os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, page_name)
    # Check in public directory (css, js, images)
    public_file = os.path.join(PUBLIC_DIR, page_name)
    if os.path.isfile(public_file):
        return send_from_directory(PUBLIC_DIR, page_name)
    return send_from_directory(FRONTEND_DIR, 'index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("Web User Behaviour Analysis - Flask Backend Server")
    print("Semester VII Progress Implementation")
    print(f"Serving on http://0.0.0.0:{port}")
    print(f"Semester VII Live Dashboard: http://localhost:{port}/dashboard")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
