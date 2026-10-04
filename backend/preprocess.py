import os
import sqlite3
import pandas as pd
import numpy as np

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'user_behavior.db')
PROCESSED_DIR = os.path.join(DB_DIR, 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

def load_raw_data():
    """Loads all tables from SQLite database into pandas DataFrames."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Please run backend/database.py first.")

    conn = sqlite3.connect(DB_PATH)
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    sessions_df = pd.read_sql_query("SELECT * FROM sessions", conn)
    page_views_df = pd.read_sql_query("SELECT * FROM page_views", conn)
    clicks_df = pd.read_sql_query("SELECT * FROM click_events", conn)
    conn.close()

    return users_df, sessions_df, page_views_df, clicks_df

def preprocess_and_engineer_features():
    """
    Cleans raw web usage tracking data using Pandas and NumPy.
    Performs feature engineering for user behavioral analysis:
    - Session duration calculation
    - Click rate / interaction intensity
    - Navigation path transition matrix
    - Composite engagement score
    """
    users_df, sessions_df, page_views_df, clicks_df = load_raw_data()

    print(f"Loaded raw records -> Users: {len(users_df)}, Sessions: {len(sessions_df)}, PageViews: {len(page_views_df)}, Clicks: {len(clicks_df)}")

    if sessions_df.empty:
        print("No session data available yet. Please populate with seed_data.py or browse the tracked app.")
        return None

    # 1. Clean Sessions Data
    sessions_df['duration_seconds'] = pd.to_numeric(sessions_df['duration_seconds'], errors='coerce').fillna(0)
    sessions_df['page_views_count'] = pd.to_numeric(sessions_df['page_views_count'], errors='coerce').fillna(1)
    sessions_df['click_count'] = pd.to_numeric(sessions_df['click_count'], errors='coerce').fillna(0)
    sessions_df['is_bounce'] = pd.to_numeric(sessions_df['is_bounce'], errors='coerce').fillna(1)

    # Convert timestamps
    sessions_df['start_time'] = pd.to_datetime(sessions_df['start_time'], errors='coerce')
    sessions_df['end_time'] = pd.to_datetime(sessions_df['end_time'], errors='coerce')

    # Derived Features using NumPy & Pandas
    # Duration in minutes
    sessions_df['duration_minutes'] = np.round(sessions_df['duration_seconds'] / 60.0, 2)

    # Click intensity (clicks per pageview)
    sessions_df['clicks_per_page'] = np.where(
        sessions_df['page_views_count'] > 0,
        np.round(sessions_df['click_count'] / sessions_df['page_views_count'], 2),
        0.0
    )

    # Dwell time per page
    sessions_df['avg_dwell_per_page'] = np.where(
        sessions_df['page_views_count'] > 0,
        np.round(sessions_df['duration_seconds'] / sessions_df['page_views_count'], 2),
        0.0
    )

    # 2. Page View Aggregations
    if not page_views_df.empty:
        page_views_df['timestamp'] = pd.to_datetime(page_views_df['timestamp'], errors='coerce')
        page_views_df['dwell_time_seconds'] = pd.to_numeric(page_views_df['dwell_time_seconds'], errors='coerce').fillna(0)
        page_views_df['scroll_depth_percent'] = pd.to_numeric(page_views_df['scroll_depth_percent'], errors='coerce').fillna(0)

        # Average scroll depth per session
        scroll_summary = page_views_df.groupby('session_id')['scroll_depth_percent'].mean().reset_index()
        scroll_summary.rename(columns={'scroll_depth_percent': 'avg_scroll_depth'}, inplace=True)
        sessions_df = sessions_df.merge(scroll_summary, on='session_id', how='left')
    else:
        sessions_df['avg_scroll_depth'] = 0.0

    sessions_df['avg_scroll_depth'] = sessions_df['avg_scroll_depth'].fillna(0.0).round(1)

    # 3. Behavioral Engagement Score (0 - 100 normalized index)
    # Composite score based on: duration, pages viewed, clicks, scroll depth
    dur_norm = np.clip(sessions_df['duration_seconds'] / 300.0, 0, 1)  # max 5 mins
    pv_norm = np.clip(sessions_df['page_views_count'] / 10.0, 0, 1)   # max 10 pages
    click_norm = np.clip(sessions_df['click_count'] / 20.0, 0, 1)     # max 20 clicks
    scroll_norm = np.clip(sessions_df['avg_scroll_depth'] / 100.0, 0, 1)

    # Weighted Formula
    engagement_index = (dur_norm * 0.3 + pv_norm * 0.3 + click_norm * 0.2 + scroll_norm * 0.2) * 100
    sessions_df['engagement_score'] = np.round(engagement_index, 1)

    # Segment users into engagement buckets (for upcoming ML clustering in Sem VIII)
    def assign_segment(score):
        if score >= 70:
            return 'High Engagement (Power User)'
        elif score >= 35:
            return 'Moderate Engagement (Explorer)'
        else:
            return 'Low Engagement (Bouncer / Casual)'

    sessions_df['behavior_segment'] = sessions_df['engagement_score'].apply(assign_segment)

    # 4. Save processed datasets for Semester VII evaluation & Semester VIII ML modeling
    clean_sessions_file = os.path.join(PROCESSED_DIR, 'clean_sessions.csv')
    sessions_df.to_csv(clean_sessions_file, index=False)

    print(f"Processed behavioral dataset saved: {clean_sessions_file}")

    # Summary Statistics
    summary = {
        "total_sessions": int(len(sessions_df)),
        "avg_duration_sec": float(sessions_df['duration_seconds'].mean()),
        "avg_pages": float(sessions_df['page_views_count'].mean()),
        "avg_clicks": float(sessions_df['click_count'].mean()),
        "bounce_rate_pct": float((sessions_df['is_bounce'].sum() / len(sessions_df)) * 100),
        "avg_engagement_score": float(sessions_df['engagement_score'].mean()),
        "segment_distribution": sessions_df['behavior_segment'].value_counts().to_dict()
    }

    return sessions_df, summary

if __name__ == '__main__':
    preprocess_and_engineer_features()
