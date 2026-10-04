import sqlite3
import os
from datetime import datetime

# Path to database file
DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'user_behavior.db')

def get_connection():
    """Returns a SQLite connection with row dictionary access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema for user tracking and behavioral analytics."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users / Visitors Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            visitor_id TEXT PRIMARY KEY,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            device_type TEXT,
            browser TEXT,
            os TEXT,
            screen_resolution TEXT
        )
    ''')

    # 2. Sessions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            visitor_id TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            duration_seconds REAL DEFAULT 0,
            page_views_count INTEGER DEFAULT 1,
            click_count INTEGER DEFAULT 0,
            is_bounce INTEGER DEFAULT 1,
            entry_page TEXT,
            exit_page TEXT,
            FOREIGN KEY (visitor_id) REFERENCES users (visitor_id)
        )
    ''')

    # 3. Page Views Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            visitor_id TEXT,
            page_url TEXT,
            page_title TEXT,
            referrer TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dwell_time_seconds REAL DEFAULT 0,
            scroll_depth_percent REAL DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id),
            FOREIGN KEY (visitor_id) REFERENCES users (visitor_id)
        )
    ''')

    # 4. Click Events Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS click_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            visitor_id TEXT,
            page_url TEXT,
            element_id TEXT,
            element_tag TEXT,
            element_class TEXT,
            element_text TEXT,
            x_pos REAL,
            y_pos REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id),
            FOREIGN KEY (visitor_id) REFERENCES users (visitor_id)
        )
    ''')

    # 5. Product Events Table (Per-Product Behavioral Tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            visitor_id TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            price REAL DEFAULT 0,
            event_type TEXT,
            dwell_time_seconds REAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id),
            FOREIGN KEY (visitor_id) REFERENCES users (visitor_id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at: {DB_PATH}")

def register_user(visitor_id, device_type='Desktop', browser='Chrome', os_name='Windows', screen_res='1920x1080'):
    """Records or updates visitor information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (visitor_id, first_seen, last_seen, device_type, browser, os, screen_resolution)
        VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?, ?)
        ON CONFLICT(visitor_id) DO UPDATE SET
            last_seen = CURRENT_TIMESTAMP,
            device_type = COALESCE(excluded.device_type, users.device_type),
            browser = COALESCE(excluded.browser, users.browser),
            os = COALESCE(excluded.os, users.os)
    ''', (visitor_id, device_type, browser, os_name, screen_res))
    conn.commit()
    conn.close()

def record_page_view(session_id, visitor_id, page_url, page_title='', referrer='', dwell_time=0, scroll_depth=0):
    """Records a page view and updates session state."""
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure session exists
    cursor.execute('SELECT session_id, page_views_count, entry_page FROM sessions WHERE session_id = ?', (session_id,))
    session = cursor.fetchone()
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if not session:
        cursor.execute('''
            INSERT INTO sessions (session_id, visitor_id, start_time, end_time, duration_seconds, page_views_count, is_bounce, entry_page, exit_page)
            VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?)
        ''', (session_id, visitor_id, now_str, now_str, dwell_time, page_url, page_url))
    else:
        new_count = session['page_views_count'] + 1
        is_bounce = 0 if new_count > 1 else 1
        cursor.execute('''
            UPDATE sessions
            SET end_time = ?,
                page_views_count = ?,
                is_bounce = ?,
                exit_page = ?
            WHERE session_id = ?
        ''', (now_str, new_count, is_bounce, page_url, session_id))

    # Insert page view
    cursor.execute('''
        INSERT INTO page_views (session_id, visitor_id, page_url, page_title, referrer, timestamp, dwell_time_seconds, scroll_depth_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, visitor_id, page_url, page_title, referrer, now_str, dwell_time, scroll_depth))

    conn.commit()
    conn.close()

def record_click_event(session_id, visitor_id, page_url, element_id, element_tag, element_class, element_text, x_pos, y_pos):
    """Records a mouse click event and increments session click count."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Update session click count
    cursor.execute('''
        UPDATE sessions
        SET click_count = click_count + 1,
            end_time = ?
        WHERE session_id = ?
    ''', (now_str, session_id))

    cursor.execute('''
        INSERT INTO click_events (session_id, visitor_id, page_url, element_id, element_tag, element_class, element_text, x_pos, y_pos, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, visitor_id, page_url, element_id, element_tag, element_class, element_text, x_pos, y_pos, now_str))

    conn.commit()
    conn.close()

def update_session_heartbeat(session_id, duration_seconds):
    """Updates session duration during active user browsing."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE sessions
        SET end_time = ?,
            duration_seconds = MAX(duration_seconds, ?)
        WHERE session_id = ?
    ''', (now_str, duration_seconds, session_id))
    conn.commit()
    conn.close()

def get_realtime_metrics():
    """Computes summary metrics for real-time progress monitoring."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) AS total_visitors FROM users')
    total_visitors = cursor.fetchone()['total_visitors']

    cursor.execute('SELECT COUNT(*) AS total_sessions, AVG(duration_seconds) AS avg_duration, AVG(page_views_count) AS avg_pages_per_session, SUM(is_bounce) AS total_bounces FROM sessions')
    session_stats = cursor.fetchone()
    total_sessions = session_stats['total_sessions'] or 0
    avg_duration = round(session_stats['avg_duration'] or 0, 1)
    avg_pages = round(session_stats['avg_pages_per_session'] or 0, 2)
    bounces = session_stats['total_bounces'] or 0
    bounce_rate = round((bounces / total_sessions * 100), 1) if total_sessions > 0 else 0.0

    cursor.execute('SELECT COUNT(*) AS total_pageviews FROM page_views')
    total_pageviews = cursor.fetchone()['total_pageviews']

    cursor.execute('SELECT COUNT(*) AS total_clicks FROM click_events')
    total_clicks = cursor.fetchone()['total_clicks']

    # Most popular pages
    cursor.execute('''
        SELECT page_url, COUNT(*) AS views, AVG(dwell_time_seconds) AS avg_dwell
        FROM page_views
        GROUP BY page_url
        ORDER BY views DESC
        LIMIT 5
    ''')
    popular_pages = [dict(row) for row in cursor.fetchall()]

    # Recent activity logs
    cursor.execute('''
        SELECT 'page_view' as type, page_url as detail, timestamp
        FROM page_views
        UNION ALL
        SELECT 'click' as type, (element_tag || ' "' || substr(COALESCE(element_text, element_id, 'element'), 1, 25) || '" on ' || page_url) as detail, timestamp
        FROM click_events
        ORDER BY timestamp DESC
        LIMIT 10
    ''')
    recent_activity = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        'total_visitors': total_visitors,
        'total_sessions': total_sessions,
        'total_pageviews': total_pageviews,
        'total_clicks': total_clicks,
        'avg_duration_seconds': avg_duration,
        'avg_pages_per_session': avg_pages,
        'bounce_rate': bounce_rate,
        'popular_pages': popular_pages,
        'recent_activity': recent_activity
    }

def record_product_event(session_id, visitor_id, product_id, product_name, category, price=0.0, event_type='view', dwell_time=0.0):
    """Records a per-product interaction event (view, detail click, add-to-cart, purchase, wishlist)."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO product_events (session_id, visitor_id, product_id, product_name, category, price, event_type, dwell_time_seconds, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, visitor_id, product_id, product_name, category, float(price), event_type, float(dwell_time), now_str))

    conn.commit()
    conn.close()

def get_product_metrics():
    """Aggregates per-product tracking metrics for analytics and visualization graphs."""
    conn = get_connection()
    cursor = conn.cursor()

    # Per-product aggregated stats
    cursor.execute('''
        SELECT 
            product_id,
            product_name,
            category,
            MAX(price) as price,
            SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
            SUM(CASE WHEN event_type IN ('click_details', 'click') THEN 1 ELSE 0 END) AS clicks,
            SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
            SUM(CASE WHEN event_type = 'buy_now' THEN 1 ELSE 0 END) AS purchases,
            SUM(CASE WHEN event_type = 'wishlist' THEN 1 ELSE 0 END) AS wishlist_count,
            ROUND(AVG(CASE WHEN dwell_time_seconds > 0 THEN dwell_time_seconds ELSE NULL END), 1) AS avg_dwell_seconds,
            COUNT(*) AS total_interactions
        FROM product_events
        GROUP BY product_id, product_name, category
        ORDER BY views DESC, total_interactions DESC
    ''')
    rows = cursor.fetchall()

    products = []
    total_views = 0
    total_cart = 0
    total_purchases = 0

    for r in rows:
        item = dict(r)
        views = item['views'] or 0
        cart = item['add_to_cart'] or 0
        purchases = item['purchases'] or 0
        conversions = cart + purchases
        conv_rate = round((conversions / views * 100.0), 1) if views > 0 else 0.0

        item['conversions'] = conversions
        item['conversion_rate'] = conv_rate
        item['avg_dwell_seconds'] = item['avg_dwell_seconds'] or 0.0

        total_views += views
        total_cart += cart
        total_purchases += purchases
        products.append(item)

    # Category-level breakdown for distribution graphs
    cursor.execute('''
        SELECT 
            category,
            SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
            SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
            SUM(CASE WHEN event_type = 'buy_now' THEN 1 ELSE 0 END) AS purchases,
            COUNT(*) AS total_events
        FROM product_events
        GROUP BY category
        ORDER BY total_events DESC
    ''')
    category_rows = [dict(c) for c in cursor.fetchall()]

    conn.close()
    return {
        'products': products,
        'categories': category_rows,
        'summary': {
            'total_product_views': total_views,
            'total_add_to_cart': total_cart,
            'total_purchases': total_purchases,
            'overall_conversion_rate': round(((total_cart + total_purchases) / total_views * 100.0), 1) if total_views > 0 else 0.0
        }
    }

if __name__ == '__main__':
    init_db()
