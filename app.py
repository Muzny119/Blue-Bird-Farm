import sqlite3
import streamlit as st

# Set Page Config
st.set_page_config(page_title="Blue Bird Farm - Accounting", page_icon="🐔", layout="wide")

# 1. Database Table Creation (Sales & Purchases)
def init_db():
    conn = sqlite3.connect('farm.db')
    c = conn.cursor()
    # Sales Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            customer_name TEXT,
            item_name TEXT,
            live_weight REAL,
            cleaned_weight REAL,
            rate REAL,
            total REAL,
            payment_method TEXT
        )
    ''')
    # Vendor Purchase Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            vendor_name TEXT,
            weight REAL,
            rate REAL,
            total REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

st.title("🐔 Blue Bird Farm - Daily Billing & Stock")

# Sidebar Tabs / Navigation
tab1, tab2, tab3 = st.tabs(["🛒 New Customer Bill", "🚚 Vendor Purchase (Chicken Buying)", "📊 Sales & Purchase Reports"])

# TAB 1: CUSTOMER BILLING
with tab1:
    st.header("📝 Customer Sales Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("Customer Name", value="Cash Customer")
        item_type = st.selectbox("Item Type", ["Live Chicken (Skinless)", "Full Chicken (Live)", "Chicken Parts", "Eggs / Other"])
        
        live_weight = st.number_input("Live Weight (in Kg)", min_value=0.0, value=2.0, step=0.1)
        
        # Auto-suggest or manual cleaned weight
        if "Skinless" in item_type:
            # Approx 30% loss for skinless chicken
            suggested_cleaned = round(live_weight * 0.70, 2)
            cleaned_weight = st.number_input("Cleaned / Skinless Weight (in Kg)", min_value=0.0, value=suggested_cleaned, step=0.05)
        else:
            cleaned_weight = live_weight

    with col2:
        rate = st.number_input("Rate per Kg (Rs)", min_value=1.0, value=240.0, step=5.0)
        
        # Calculate bill based on cleaned weight or live weight option
        rate_basis = st.radio("Rate Applied On", ["Cleaned Weight", "Live Weight"])
        
        if rate_basis == "Cleaned Weight":
            total_amount = cleaned_weight * rate
        else:
            total_amount = live_weight * rate
            
        st.markdown(f"### 💵 Total Amount: **Rs. {total_amount:.2f}**")
        payment_method = st.radio("Payment Method", ["Cash", "Online/Bank Transfer", "Credit (Kadan)"])

    if st.button("Save Sales Transaction", use_container_width=True):
        conn = sqlite3.connect('farm.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO sales (date, customer_name, item_name, live_weight, cleaned_weight, rate, total, payment_method)
            VALUES (date('now'), ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_name, item_type, live_weight, cleaned_weight, rate, total_amount, payment_method))
        conn.commit()
        conn.close()
        st.success(f"Sale recorded for {customer_name}! Total: Rs.{total_amount:.2f} 🎉")

# TAB 2: VENDOR PURCHASES
with tab2:
    st.header("🚚 Vendor Purchase Entry (Buying Live Stock)")
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        vendor_name = st.text_input("Vendor / Supplier Name", placeholder="e.g. John Poultry / Farm A")
        purchase_weight = st.number_input("Total Live Weight Bought (Kg)", min_value=0.1, value=50.0, step=1.0)
        
    with col_v2:
        purchase_rate = st.number_input("Purchase Rate per Kg (Rs)", min_value=1.0, value=180.0, step=2.0)
        purchase_total = purchase_weight * purchase_rate
        st.markdown(f"### 🧾 Purchase Total: **Rs. {purchase_total:.2f}**")

    if st.button("Save Purchase Record", use_container_width=True):
        if vendor_name.strip() == "":
            st.error("Please enter a Vendor Name!")
        else:
            conn = sqlite3.connect('farm.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO purchases (date, vendor_name, weight, rate, total)
                VALUES (date('now'), ?, ?, ?, ?)
            ''', (vendor_name, purchase_weight, purchase_rate, purchase_total))
            conn.commit()
            conn.close()
            st.success(f"Purchase from {vendor_name} saved successfully! 🎉")

# TAB 3: REPORTS & RECORDS
with tab3:
    st.header("📊 Transaction History & Reports")
    
    st.subheader("🛒 Customer Sales History")
    conn = sqlite3.connect('farm.db')
    c = conn.cursor()
    c.execute("SELECT date, customer_name, item_name, live_weight, cleaned_weight, rate, total, payment_method FROM sales ORDER BY id DESC")
    sales_data = c.fetchall()
    
    if sales_data:
        st.dataframe(
            sales_data,
            column_config={
                "0": "Date",
                "1": "Customer Name",
                "2": "Item Type",
                "3": "Live Wt (Kg)",
                "4": "Cleaned Wt (Kg)",
                "5": "Rate (Rs)",
                "6": "Total (Rs)",
                "7": "Payment"
            },
            use_container_width=True
        )
    else:
        st.info("No sales records found.")

    st.markdown("---")
    
    st.subheader("🚚 Vendor Purchase History")
    c.execute("SELECT date, vendor_name, weight, rate, total FROM purchases ORDER BY id DESC")
    purchase_data = c.fetchall()
    conn.close()
    
    if purchase_data:
        st.dataframe(
            purchase_data,
            column_config={
                "0": "Date",
                "1": "Vendor Name",
                "2": "Weight Bought (Kg)",
                "3": "Buy Rate (Rs)",
                "4": "Total Paid (Rs)"
            },
            use_container_width=True
        )
    else:
        st.info("No vendor purchase records found.")
