import sqlite3

# Auto-create database table if not exists
conn = sqlite3.connect('farm.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        item_name TEXT,
        weight REAL,
        rate REAL,
        total REAL,
        payment_method TEXT
    )
''')
conn.commit()
conn.close()import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Configuration - Blue Bird Farm
st.set_page_config(page_title="Blue Bird Farm - Accounting", layout="wide", page_icon="🐔")

st.title("🐔 Blue Bird Farm - Poultry Accounting System")
st.caption("Daily Sales, Billing & Stock Tracking")

def get_connection():
    return sqlite3.connect("poultry_shop.db")

col1, col2 = st.columns([1, 2])

# --- COLUMN 1: Bill Entry ---
with col1:
    st.header("📝 New Bill Entry")
    
    item_name = st.selectbox("Item Type", ["Whole Chicken", "Skinless", "Leg Piece", "Breast", "Liver/Gizzard", "Live Birds"])
    weight = st.number_input("Weight (in Kg)", min_value=0.1, step=0.1, value=1.0)
    rate = st.number_input("Today Rate per Kg (Rs)", min_value=1.0, step=5.0, value=240.0)
    payment_type = st.radio("Payment Method", ["Cash", "Online/Bank Transfer", "Credit (Kadan)"])
    
    total = weight * rate
    st.markdown(f"### **Total Amount: Rs. {total:.2f}**")
    
    if st.button("Save Transaction"):
        today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (date, item_name, weight_kg, price_per_kg, total_amount, payment_type) VALUES (?, ?, ?, ?, ?, ?)",
            (today_date, item_name, weight, rate, total, payment_type)
        )
        conn.commit()
        conn.close()
        st.success("Entry Saved to Blue Bird Farm Database!")

# --- COLUMN 2: Sales Records ---
with col2:
    st.header("📊 Sales & Summary")
    
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM sales ORDER BY id DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        total_income = df["total_amount"].sum()
        total_weight = df["weight_kg"].sum()
        
        st.subheader("Today's Summary")
        sub_col1, sub_col2 = st.columns(2)
        sub_col1.metric("Total Sales Amount", f"Rs. {total_income:.2f}")
        sub_col2.metric("Total Weight Sold", f"{total_weight:.2f} Kg")
    else:
        st.info("No sales recorded yet. Save an entry on the left side!")
