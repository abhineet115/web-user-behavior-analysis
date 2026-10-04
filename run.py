"""
Web User Behaviour Analysis - Project Runner
Semester VII Progress Deliverable
ITS Engineering College, Greater Noida • AKTU
"""

import sys
import os
import webbrowser

import sys
import os

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add backend directory to python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)

import database
import seed_data
from app import app

def main():
    print("=" * 70)
    print(">> WEB USER BEHAVIOUR ANALYSIS USING MACHINE LEARNING")
    print(">> SEMESTER VII PROGRESS DEMONSTRATION")
    print(">> ITS Engineering College, Greater Noida - AKTU")
    print("=" * 70)

    # 1. Initialize SQLite Database
    print("\n[Step 1] Initializing Relational Database Schema...")
    database.init_db()

    # 2. Check if database has data, if not seed initial demonstration data
    metrics = database.get_realtime_metrics()
    if metrics['total_sessions'] < 5:
        print("[Step 2] Database is empty. Seeding realistic sample user journeys for demo...")
        seed_data.seed_database(num_visitors=25)
    else:
        print(f"[Step 2] Existing records detected: {metrics['total_visitors']} visitors, {metrics['total_sessions']} sessions.")

    # 3. Print URLs
    print("\n" + "=" * 70)
    print(">> PLATFORM IS READY AND LISTENING:")
    print(">> Tracked Web Application (Frontend) : http://localhost:5000")
    print(">> Semester VII Progress Dashboard    : http://localhost:5000/dashboard")
    print(">> Backend REST API Endpoint          : http://localhost:5000/api/track/init")
    print("=" * 70 + "\n")

    # Start Flask Server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
