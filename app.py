import sqlite3
import streamlit as st

# 1. Database Table Creation
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
conn.close()

# 2. Streamlit UI Design
st.set_page_config(page_title="Blue Bird Farm - Accounting", page_icon="📝")

st.title("📝 New Bill Entry")

item_type = st.selectbox("Item Type", ["Whole Chicken", "Chicken Breast", "Chicken Leg", "Other"])
weight = st.number_input("Weight (in Kg)", min_value=0.1, value=1.0, step=0.1)
rate = st.number_input("Today Rate per Kg (Rs)", min_value=1.0, value=240.0, step=5.0)

payment_method = st.radio("Payment Method", ["Cash", "Online/Bank Transfer", "Credit (Kadan)"])

total_amount = weight * rate
st.subheader(f"Total Amount: Rs. {total_amount:.2f}")

if st.button("Save Transaction"):
    conn = sqlite3.connect('farm.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO sales (date, item_name, weight, rate, total, payment_method)
        VALUES (date('now'), ?, ?, ?, ?, ?)
    ''', (item_type, weight, rate, total_amount, payment_method))
    conn.commit()
    conn.close()
    st.success("Transaction Saved Successfully! 🎉")

st.markdown("---")
st.header("📊 Sales & Summary")

# Display Existing Records
conn = sqlite3.connect('farm.db')
c = conn.cursor()
c.execute("SELECT date, item_name, weight, rate, total, payment_method FROM sales ORDER BY id DESC")
rows = c.fetchall()
conn.close()

if rows:
    st.dataframe(rows, column_config={
        "0": "Date",
        "1": "Item",
        "2": "Weight (Kg)",
        "3": "Rate (Rs)",
        "4": "Total (Rs)",
        "5": "Payment"
    })
else:
    st.info("No sales recorded yet. Save an entry on the left side!")
