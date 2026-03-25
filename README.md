# 💜 PhonePe Transaction Insights — EDA Project

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red)
![Plotly](https://img.shields.io/badge/Plotly-6.6-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📌 Project Overview

This project analyzes PhonePe's digital payment transaction data sourced from the official **PhonePe Pulse GitHub repository**. It covers transaction patterns, user engagement, device usage, insurance adoption, and geographic distribution across all 36 Indian states and union territories from **2018 to 2024**.

The project includes:
- A full **ETL pipeline** that extracts nested JSON data and loads it into PostgreSQL
- **15 SQL queries** across 5 business case studies
- A **Jupyter notebook** with 22 interactive Plotly charts and business insights
- A **Streamlit dashboard** with dynamic filters for real-time data exploration

---

## 🎯 Business Case Studies Covered

| # | Case Study | Key Finding |
|---|---|---|
| 1 | Transaction Dynamics | Merchant payments dominate volume but P2P moves 4x more money |
| 2 | Device & User Engagement | Xiaomi + Vivo + Samsung = 62% of all PhonePe users |
| 3 | Insurance Penetration | Insurance value grew 27x from 2020-2024 but penetration below 0.05% |
| 7 | District Level Analysis | Bengaluru Urban alone outperforms entire states |
| 8 | User Registration | NCR dominates registrations but has critically low engagement |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.8+ | Data extraction, transformation, analysis |
| PostgreSQL | Relational database for storing 116,749 rows across 9 tables |
| Pandas | Data manipulation and cleaning |
| Plotly | Interactive visualizations |
| Streamlit | Interactive dashboard |
| SQLAlchemy | Database connection and querying |
| psycopg2 | PostgreSQL adapter for Python |
| Git | Version control |

---

## 📁 Project Structure

```
PhonePe-Transaction-Insights-EDA/
│
├── scripts/
│   ├── etl.py              # ETL pipeline — JSON to PostgreSQL
│   └── analysis.sql        # 15 SQL queries across 5 case studies
│
├── notebooks/
│   └── phonepe_eda.ipynb   # EDA notebook with 22 charts
│
├── dashboard/
│   ├── app.py              # Streamlit dashboard
│   └── assets/
│       └── phonepe_logo.png
│
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

---

## 🗄️ Database Schema

The ETL pipeline creates 9 tables in PostgreSQL:

| Table | Rows | Description |
|---|---|---|
| aggregated_transaction | 5,174 | Payment category wise transactions at state level |
| aggregated_user | 6,919 | Registered users and device brand data at state level |
| aggregated_insurance | 701 | Insurance transactions at state level |
| map_transaction | 20,604 | District level transaction data |
| map_user | 20,608 | District level user registration data |
| map_insurance | 13,876 | District level insurance data |
| top_transaction | 18,295 | Top districts and pin codes by transactions |
| top_user | 18,296 | Top districts and pin codes by registered users |
| top_insurance | 12,276 | Top districts and pin codes by insurance |
| **Total** | **116,749** | |

---

## ⚙️ How to Run This Project

### Prerequisites
Make sure you have these installed:
- Python 3.8 or higher
- PostgreSQL 13 or higher
- Git

---

### Step 1 — Clone this repository
```bash
git clone https://github.com/nilesh29b/PhonePe-Transaction-Insights-EDA.git
cd PhonePe-Transaction-Insights-EDA
```

### Step 2 — Clone the PhonePe Pulse data
```bash
git clone https://github.com/PhonePe/pulse.git
```
> ⚠️ This is ~500MB. Make sure you have enough disk space and a stable internet connection.

### Step 3 — Create and activate virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Set up PostgreSQL database
Open PostgreSQL and create the database:
```sql
CREATE DATABASE phonepe_pulse;
```

### Step 6 — Update database credentials
Open `scripts/etl.py` and update these lines with your PostgreSQL credentials:
```python
DB_USER = "postgres"
DB_PASSWORD = "your_password_here"  # ← change this
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "phonepe_pulse"
```

Also update the `BASE_PATH` to point to your cloned pulse data:
```python
BASE_PATH = r"path\to\your\pulse\data"
```

Do the same in `dashboard/app.py`.

### Step 7 — Run the ETL pipeline
```bash
python scripts/etl.py
```
Expected output:
```
✅ aggregated_transaction: 5174 rows loaded successfully
✅ aggregated_user: 6919 rows loaded successfully
✅ aggregated_insurance: 701 rows loaded successfully
✅ map_transaction: 20604 rows loaded successfully
✅ map_user: 20608 rows loaded successfully
✅ map_insurance: 13876 rows loaded successfully
✅ top_transaction: 18295 rows loaded successfully
✅ top_user: 18296 rows loaded successfully
✅ top_insurance: 12276 rows loaded successfully
ETL Pipeline Complete!
```

### Step 8 — Run the Streamlit dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`

### Step 9 — Run the EDA notebook
Open `notebooks/phonepe_eda.ipynb` in VS Code or Jupyter and select the `phonepe_venv` kernel.

---

## 📊 Dashboard Features

The Streamlit dashboard has 5 pages:

| Page | Description |
|---|---|
| 🏠 Overview | Key metrics, YoY growth, category distribution |
| 💳 Transaction Analysis | Top states by volume and value, category breakdown |
| 👥 User & Device Analysis | Device brand treemap, engagement by state, scatter plot |
| 🗺️ District Deep Dive | Top 15 districts filtered by state |
| 🛡️ Insurance Analysis | Insurance growth trajectory, top states |

**Filters available:**
- Year (2018–2024)
- Quarter (Q1–Q4)
- State (all 36 states and UTs)
- Clear All Filters button

---

## 🔍 Key Insights

1. **Merchant payments dominate volume (55%) but P2P dominates value (₹266 trillion)** — PhonePe users make frequent small merchant payments but move large amounts through P2P transfers.

2. **Transaction growth rate declining but absolute numbers exploding** — Growth rate fell from 277% (2019) to 54% (2024) but absolute transactions grew from 1B to 99B. Classic law of large numbers.

3. **Telangana is the biggest insurance opportunity** — 3rd largest transaction state but lowest insurance penetration (0.0174%). 25 billion active transactions, almost no insurance usage.

4. **NCR paradox** — 7 of top 10 registered user pin codes are in NCR (Noida, Delhi, Gurugram) but Delhi has only 16.5 opens per user — well below national median of 22.

5. **Bengaluru Urban is PhonePe's most reliable market** — 86x transaction growth from 2018 to 2024 with perfectly consistent year over year growth. No anomalies.

---

## ⚠️ Data Quality Notes

1. Insurance data starts from **2020 Q2** — Q1 2020 is missing
2. Hyderabad district shows anomalous spike in 2022 — likely district boundary reclassification
3. Ahmedabad district has two spellings in source data — "ahmedabad" and "ahmadabad"
4. Device brand data drops sharply after 2021 — reporting methodology change
5. `aggregated_transaction` contains an 'india' summary row — excluded from all state level calculations

---

## 💡 Business Recommendations

1. **Launch targeted insurance campaigns in Telangana** — highest transaction volume, lowest insurance penetration
2. **Re-engagement campaign for NCR pin codes** — millions of registered but dormant users
3. **Pre-installation partnership with Xiaomi and Vivo** — together control 43% of user base
4. **Merchant acquisition drive in Rangareddy district** — fastest growing district nationally (172x growth 2018-2024)
5. **Q4 insurance bundle campaign** — insurance spikes in Q4 with festive season, align product launches accordingly

---

## 📄 Data Source

**PhonePe Pulse GitHub Repository:**
https://github.com/PhonePe/pulse

---

## 👤 Author

**Nilesh**
- GitHub: [@nilesh29b](https://github.com/nilesh29b)

---

## 📝 License

This project is for educational purposes only. PhonePe Pulse data is owned by PhonePe and used under their open data policy.
