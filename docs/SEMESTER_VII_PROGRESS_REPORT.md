# SEMESTER VII PROJECT PROGRESS REPORT
## WEB USER BEHAVIOUR ANALYSIS USING MACHINE LEARNING

**Academic Session:** 2026–2027  
**Department:** Computer Science and Engineering  
**Institution:** ITS Engineering College, Greater Noida – 201306  
**Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow  

---

### Project Details & Team
- **Project Title:** Web User Behaviour Analysis Using Machine Learning
- **Project Supervisor:** Mr. Manik Chandra Panday
- **Team Members:**
  1. Abhineet Kr Sinha (Roll No: 2302220100009)
  2. Viswajeet Kr Singh (Roll No: 2302220100010)
  3. Sanjeet Kumar (Roll No: 2302220100163)
  4. Amrit Raj (Roll No: 2302220100032)

---

## 1. Executive Summary & Semester VII Progress Objectives
In Semester VII, the focus was to establish the complete architectural foundation, database schema, data collection framework, and preprocessing pipeline for the **Web User Behaviour Analysis** system.

### Key Milestones Completed in Semester VII:
1. **Literature Survey & Research Gap Identification:** Reviewed foundational studies (Srivastava et al. 2000, Mobasher et al. 2000, Kosala & Blockeel 2000) and pinpointed the need for a unified open-source analytics platform.
2. **System Design & Tier Separation:** Completely decoupled Frontend and Backend into independent, modular architectures.
3. **Database Architecture:** Designed and implemented relational database schemas in SQLite/MySQL covering Visitors, Sessions, Page Views, and Clickstream interactions.
4. **Client-Side Behavioral Tracking Engine (`tracker.js`):** Built a non-intrusive client-side tracking script capable of tracking visitor IDs, session lifecycles, mouse click coordinates, element selectors, dwell durations, and scroll depths.
5. **Backend REST Ingestion Server (`app.py` / Flask):** Created high-throughput REST API endpoints for receiving real-time beacons and session heartbeats.
6. **Data Preprocessing & Feature Engineering (`preprocess.py`):** Developed automated Pandas and NumPy routines to clean raw interaction data, derive engagement metrics, and calculate behavioral scores (0–100).
7. **Semester VII Progress Live Dashboard (`sem7_dashboard.html`):** Developed an interactive evaluation monitor displaying real-time metrics, live activity feeds, and preprocessed behavioral segmentations.

---

## 2. Semester VII vs Semester VIII Milestone Status (Activity Chart)

| Activity | Semester VII Status | Semester VIII Target |
| :--- | :---: | :---: |
| Project Topic Selection | **100% Completed** | Completed |
| Literature Survey | **100% Completed** | Completed |
| Requirement Analysis | **100% Completed** | Completed |
| System & Database Design | **100% Completed** | Completed |
| Frontend Development (Phase 1) | **100% Completed** | Polish & UI enhancements |
| Backend Development (Phase 1) | **100% Completed** | ML endpoint integrations |
| Database Integration | **100% Completed** | Scale & optimization |
| Data Collection & Preprocessing | **100% Completed** | Scaled ingestion |
| Machine Learning Model Development | *Foundations Prepared* | **K-Means / DBSCAN / Markov Models** |
| Dashboard Development (Streamlit / Web) | *Sem VII Monitor Built* | **Streamlit Advanced Visuals** |
| Testing & Bug Fixing | Unit & Flow Tested | Rigorous stress testing |
| Final Deployment & Viva | Local Dev Server Ready | **Render/Heroku Deployment & Final Viva** |

---

## 3. System Architecture & Technical Specifications

### Architecture Pipeline
```
[User Browser Interactions]
         │ (Clicks, Dwell, Scroll, Paths)
         ▼
[tracker.js (Client Engine)]
         │ POST JSON Payloads
         ▼
[Flask REST Ingestion APIs (/api/track)]
         │ SQL Transactions
         ▼
[Relational Database (user_behavior.db)]
  ├── users
  ├── sessions
  ├── page_views
  └── click_events
         │
         ▼
[Pandas & NumPy Preprocessing Pipeline]
  ├── Missing value handling & type casting
  ├── Session duration & click intensity calculation
  ├── Composite Engagement Index (0-100)
  └── Behavioral Segmentation (High, Moderate, Bouncer)
         │
         ▼
[Semester VII Progress Evaluation Dashboard]
```

### Technology Stack
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Backend:** Python Flask
- **Database:** SQLite3 / MySQL compatible relational schema
- **Data Engineering:** Pandas, NumPy
- **Visuals & Progress Monitor:** Custom Dark UI, Chart abstractions, Real-time DOM poller

---

## 4. Alignment with UN Sustainable Development Goals (SDGs)
- **SDG 9 (Industry, Innovation & Infrastructure):** Builds an accessible, open-source web usage analytics platform empowering educational and small-scale digital systems without licensing friction.
- **SDG 8 (Decent Work & Economic Growth):** Provides actionable insights into user journeys and digital usability, boosting operational efficiency and digital service quality.

---

## 5. Conclusion & Transition to Semester VIII
Semester VII has successfully delivered a fully functional tracking and data preprocessing ecosystem. The project is on schedule to enter Semester VIII, where machine learning algorithms (unsupervised behavioral clustering, navigation prediction, and Streamlit-based graphical dashboards) will be trained on the clean datasets established in this phase.
