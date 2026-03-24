# =============================================================
# PhonePe Pulse - ETL Pipeline
# Purpose: Extract data from JSON files, transform it into
#          structured tables, and load into PostgreSQL
# =============================================================

import os
import json
import pandas as pd
from sqlalchemy import create_engine 

# =============================================================
# DATABASE CONNECTION
# Why: We create one engine and reuse it for all table loads.
#      SQLAlchemy handles the connection pooling cleanly.
# =============================================================

DB_USER = "postgres"
DB_PASSWORD = "1234"   # ← change this to your PostgreSQL password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "phonepe_pulse"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# =============================================================
# BASE PATH
# Why: All JSON files live inside pulse/data. We set this once
#      so every function below can build paths from it.
# =============================================================

BASE_PATH = r"C:\Users\ASUS\OneDrive\Desktop\phonepe_project\pulse\data"


# =============================================================
# TABLE 1 - AGGREGATED TRANSACTION
# Source: aggregated/transaction/country/india/
# What it contains: Payment category wise transaction count
#                   and amount at india and state level,
#                   by year and quarter
# =============================================================

def extract_aggregated_transaction():
    """
    Walks through aggregated/transaction folder.
    Each JSON file = one quarter of data for one state or india.
    Returns a DataFrame with one row per payment category per quarter.
    """
    records = []

    # We loop through both india level and state level data
    base = os.path.join(BASE_PATH, "aggregated", "transaction", "country", "india")

    # --- India level ---
    for year in os.listdir(base):
        year_path = os.path.join(base, year)
        # Skip the 'state' folder, only process year folders (numeric names)
        if not year.isdigit():
            continue
        for quarter_file in os.listdir(year_path):
            quarter = quarter_file.replace(".json", "")
            file_path = os.path.join(year_path, quarter_file)
            with open(file_path, "r") as f:
                data = json.load(f)
            # Navigate into the nested structure
            transaction_list = data["data"]["transactionData"]
            for item in transaction_list:
                records.append({
                    "state": "india",
                    "year": int(year),
                    "quarter": int(quarter),
                    "transaction_type": item["name"],
                    "transaction_count": item["paymentInstruments"][0]["count"],
                    "transaction_amount": item["paymentInstruments"][0]["amount"]
                })

    # --- State level ---
    state_path = os.path.join(base, "state")
    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                transaction_list = data["data"]["transactionData"]
                for item in transaction_list:
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "transaction_type": item["name"],
                        "transaction_count": item["paymentInstruments"][0]["count"],
                        "transaction_amount": item["paymentInstruments"][0]["amount"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 2 - AGGREGATED USER
# Source: aggregated/user/country/india/
# What it contains: Registered users and app opens,
#                   plus device brand breakdown
# =============================================================

def extract_aggregated_user():
    """
    Walks through aggregated/user folder.
    Returns a DataFrame with one row per device brand per quarter.
    """
    records = []

    base = os.path.join(BASE_PATH, "aggregated", "user", "country", "india")

    # --- India level ---
    for year in os.listdir(base):
        year_path = os.path.join(base, year)
        if not year.isdigit():
            continue
        for quarter_file in os.listdir(year_path):
            quarter = quarter_file.replace(".json", "")
            file_path = os.path.join(year_path, quarter_file)
            with open(file_path, "r") as f:
                data = json.load(f)
            # Some files may have null usersByDevice
            users_by_device = data["data"].get("usersByDevice") or []
            registered_users = data["data"]["aggregated"]["registeredUsers"]
            app_opens = data["data"]["aggregated"]["appOpens"]
            for device in users_by_device:
                records.append({
                    "state": "india",
                    "year": int(year),
                    "quarter": int(quarter),
                    "registered_users": registered_users,
                    "app_opens": app_opens,
                    "device_brand": device["brand"],
                    "device_count": device["count"],
                    "device_percentage": device["percentage"]
                })

    # --- State level ---
    state_path = os.path.join(base, "state")
    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                users_by_device = data["data"].get("usersByDevice") or []
                registered_users = data["data"]["aggregated"]["registeredUsers"]
                app_opens = data["data"]["aggregated"]["appOpens"]
                for device in users_by_device:
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "registered_users": registered_users,
                        "app_opens": app_opens,
                        "device_brand": device["brand"],
                        "device_count": device["count"],
                        "device_percentage": device["percentage"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 3 - AGGREGATED INSURANCE
# Source: aggregated/insurance/country/india/
# What it contains: Insurance transaction count and amount
# Note: Data starts from 2020 Q2, not 2018
# =============================================================

def extract_aggregated_insurance():
    """
    Walks through aggregated/insurance folder.
    Returns a DataFrame with one row per quarter per state.
    """
    records = []

    base = os.path.join(BASE_PATH, "aggregated", "insurance", "country", "india")

    # --- India level ---
    for year in os.listdir(base):
        year_path = os.path.join(base, year)
        if not year.isdigit():
            continue
        for quarter_file in os.listdir(year_path):
            quarter = quarter_file.replace(".json", "")
            file_path = os.path.join(year_path, quarter_file)
            with open(file_path, "r") as f:
                data = json.load(f)
            transaction_list = data["data"]["transactionData"]
            for item in transaction_list:
                records.append({
                    "state": "india",
                    "year": int(year),
                    "quarter": int(quarter),
                    "transaction_type": item["name"],
                    "transaction_count": item["paymentInstruments"][0]["count"],
                    "transaction_amount": item["paymentInstruments"][0]["amount"]
                })

    # --- State level ---
    state_path = os.path.join(base, "state")
    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                transaction_list = data["data"]["transactionData"]
                for item in transaction_list:
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "transaction_type": item["name"],
                        "transaction_count": item["paymentInstruments"][0]["count"],
                        "transaction_amount": item["paymentInstruments"][0]["amount"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 4 - MAP TRANSACTION
# Source: map/transaction/hover/country/india/
# What it contains: District level transaction count and amount
#                   per state, per year and quarter
# =============================================================

def extract_map_transaction():
    """
    Walks through map/transaction folder.
    Returns a DataFrame with one row per district per quarter.
    """
    records = []

    state_path = os.path.join(BASE_PATH, "map", "transaction", "hover", "country", "india", "state")

    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                district_list = data["data"]["hoverDataList"]
                for district in district_list:
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "district": district["name"],
                        "transaction_count": district["metric"][0]["count"],
                        "transaction_amount": district["metric"][0]["amount"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 5 - MAP USER
# Source: map/user/hover/country/india/
# What it contains: District level registered users and app opens
# =============================================================

def extract_map_user():
    """
    Walks through map/user folder.
    Returns a DataFrame with one row per district per quarter.
    """
    records = []

    state_path = os.path.join(BASE_PATH, "map", "user", "hover", "country", "india", "state")

    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                district_list = data["data"]["hoverData"]
                for district_name, district_data in district_list.items():
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "district": district_name,
                        "registered_users": district_data["registeredUsers"],
                        "app_opens": district_data["appOpens"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 6 - MAP INSURANCE
# Source: map/insurance/hover/country/india/
# What it contains: District level insurance transaction data
# =============================================================

def extract_map_insurance():
    """
    Walks through map/insurance folder.
    Returns a DataFrame with one row per district per quarter.
    """
    records = []

    state_path = os.path.join(BASE_PATH, "map", "insurance", "hover", "country", "india", "state")

    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                district_list = data["data"]["hoverDataList"]
                for district in district_list:
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "district": district["name"],
                        "transaction_count": district["metric"][0]["count"],
                        "transaction_amount": district["metric"][0]["amount"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 7 - TOP TRANSACTION
# Source: top/transaction/country/india/
# What it contains: Top performing districts and pin codes
#                   by transaction count and amount
# =============================================================

def extract_top_transaction():
    """
    Walks through top/transaction folder.
    Returns a DataFrame with top districts and pincodes per quarter.
    """
    records = []

    state_path = os.path.join(BASE_PATH, "top", "transaction", "country", "india", "state")

    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                # Top districts
                for item in data["data"].get("districts", []):
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "entity_type": "district",
                        "entity_name": item["entityName"],
                        "transaction_count": item["metric"]["count"],
                        "transaction_amount": item["metric"]["amount"]
                    })
                # Top pincodes
                for item in data["data"].get("pincodes", []):
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "entity_type": "pincode",
                        "entity_name": item["entityName"],
                        "transaction_count": item["metric"]["count"],
                        "transaction_amount": item["metric"]["amount"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 8 - TOP USER
# Source: top/user/country/india/
# What it contains: Top districts and pincodes by registered users
# =============================================================

def extract_top_user():
    """
    Walks through top/user folder.
    Returns a DataFrame with top districts and pincodes by users.
    """
    records = []

    state_path = os.path.join(BASE_PATH, "top", "user", "country", "india", "state")

    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                for item in data["data"].get("districts", []):
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "entity_type": "district",
                        "entity_name": item["name"],
                        "registered_users": item["registeredUsers"]
                    })
                for item in data["data"].get("pincodes", []):
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "entity_type": "pincode",
                        "entity_name": item["name"],
                        "registered_users": item["registeredUsers"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# TABLE 9 - TOP INSURANCE
# Source: top/insurance/country/india/
# What it contains: Top districts and pincodes by insurance
# =============================================================

def extract_top_insurance():
    """
    Walks through top/insurance folder.
    Returns a DataFrame with top districts and pincodes by insurance.
    """
    records = []

    state_path = os.path.join(BASE_PATH, "top", "insurance", "country", "india", "state")

    for state in os.listdir(state_path):
        state_year_path = os.path.join(state_path, state)
        for year in os.listdir(state_year_path):
            if not year.isdigit():
                continue
            year_path = os.path.join(state_year_path, year)
            for quarter_file in os.listdir(year_path):
                quarter = quarter_file.replace(".json", "")
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                for item in data["data"].get("districts", []):
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "entity_type": "district",
                        "entity_name": item["entityName"],
                        "transaction_count": item["metric"]["count"],
                        "transaction_amount": item["metric"]["amount"]
                    })
                for item in data["data"].get("pincodes", []):
                    records.append({
                        "state": state,
                        "year": int(year),
                        "quarter": int(quarter),
                        "entity_type": "pincode",
                        "entity_name": item["entityName"],
                        "transaction_count": item["metric"]["count"],
                        "transaction_amount": item["metric"]["amount"]
                    })

    df = pd.DataFrame(records)
    return df


# =============================================================
# LOAD TO POSTGRESQL
# Why: if_exists="replace" means every time you run this script,
#      it drops the old table and recreates it fresh.
#      This is safe during development. Change to "append"
#      only if you want to add rows without wiping the table.
# =============================================================

def load_to_db(df, table_name):
    """
    Loads a DataFrame into PostgreSQL.
    Prints row count confirmation after loading.
    """
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"✅ {table_name}: {len(df)} rows loaded successfully")


# =============================================================
# MAIN - Run all extractions and loads in sequence
# =============================================================

if __name__ == "__main__":
    print("Starting ETL Pipeline...\n")

    print("Extracting Aggregated Transaction...")
    load_to_db(extract_aggregated_transaction(), "aggregated_transaction")

    print("Extracting Aggregated User...")
    load_to_db(extract_aggregated_user(), "aggregated_user")

    print("Extracting Aggregated Insurance...")
    load_to_db(extract_aggregated_insurance(), "aggregated_insurance")

    print("Extracting Map Transaction...")
    load_to_db(extract_map_transaction(), "map_transaction")

    print("Extracting Map User...")
    load_to_db(extract_map_user(), "map_user")

    print("Extracting Map Insurance...")
    load_to_db(extract_map_insurance(), "map_insurance")

    print("Extracting Top Transaction...")
    load_to_db(extract_top_transaction(), "top_transaction")

    print("Extracting Top User...")
    load_to_db(extract_top_user(), "top_user")

    print("Extracting Top Insurance...")
    load_to_db(extract_top_insurance(), "top_insurance")

    print("\nETL Pipeline Complete!")