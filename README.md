# Web User Behaviour Analysis Using Machine Learning
**Final Year Project • Semester VII Progress**  
*Department of Computer Science & Engineering — ITS Engineering College, Greater Noida (AKTU)*

---

## 📌 Project Overview
Web User Behaviour Analysis is an end-to-end web analytics and intelligence platform designed to capture, process, and analyze visitor interaction data. 

In **Semester VII**, the full foundational pipeline has been established:
- **Clean Separation:** Frontend and Backend are decoupled into separate, organized directories.
- **Client-Side Behavioral Tracking (`tracker.js`):** Collects sessions, page views, click coordinates, element tags/classes, scroll depth, and dwell duration.
- **Flask REST Ingestion Engine (`app.py`):** High-speed ingestion APIs and static serving.
- **Relational Schema (`database.py`):** SQLite schema storing users, sessions, pageviews, and clicks.
- **Preprocessing Pipeline (`preprocess.py`):** Clean data transformations using Pandas and NumPy, calculating bounce rates, click intensities, and composite engagement scores.
- **Live Monitoring Dashboard (`sem7_dashboard.html`):** Real-time project evaluation dashboard for viva and presentation.

> 📖 **Comprehensive Master Project Documentation:**  
> For the complete, in-depth architectural guide, script placement handbook, machine learning roadmap, 7th Semester integration details, and monthly report generation templates, please see [1.md](file:///c:/Users/CODE15/Documents/GitHub/Web%20User%20Behavior%20Analysis/1.md).


---

## 🗂️ Project Directory Structure
```text
Web User Behavior Analysis/
│
├── frontend/                     # Completely decoupled Frontend
│   ├── public/                   # Client-side static assets
│   │   ├── css/
│   │   │   ├── style.css         # Tracked website styling
│   │   │   └── dashboard.css     # Sem VII Monitor dark UI
│   │   └── js/
│   │       ├── tracker.js        # Core behavioral tracking engine
│   │       └── dashboard.js      # Dashboard controller & live poller
│   ├── index.html                # Tracked Website Home
│   ├── products.html             # Products catalog
│   ├── product-details.html      # Product detail & conversion actions
│   ├── blog.html                 # Long-form article (scroll depth & dwell test)
│   ├── contact.html              # Feedback form (input & submit tracking)
│   └── sem7_dashboard.html       # Semester VII Progress Evaluation Dashboard
│
├── backend/                      # Completely decoupled Backend
│   ├── app.py                    # Flask server & REST APIs
│   ├── database.py               # SQLite schema & SQL execution methods
│   ├── preprocess.py             # Pandas & NumPy data engineering pipeline
│   ├── seed_data.py              # Synthetic visitor traffic generator
│   └── data/                     # Database file & processed CSV outputs
│
├── docs/                         # Project Documentation
│   └── SEMESTER_VII_PROGRESS_REPORT.md  # Formal Semester VII Progress Report
│
├── requirements.txt              # Python library dependencies
├── run.py                        # Single-command project launcher
└── README.md                     # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python run.py
```

### 3. Open in Browser
- **Live Tracked Website (Frontend):** [http://localhost:5000](http://localhost:5000)
- **Semester VII Progress Dashboard:** [http://localhost:5000/dashboard](http://localhost:5000/dashboard)

---

## 👥 Project Team
- **Abhineet Kr Sinha** (2302220100009)
- **Viswajeet Kr Singh** (2302220100010)
- **Sanjeet Kumar** (2302220100163)
- **Amrit Raj** (2302220100032)
- **Supervisor:** Mr. Manik Chandra Panday
