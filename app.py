import sqlite3
import streamlit as st

st.set_page_config(page_title="Blue Bird Farm - Accounting", page_icon="🐔", layout="wide")

# Database Setup (Using fresh database name to fix schema mismatch)
DB_FILE = 'farm_v2.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Vendor Purchases Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            vendor_name TEXT,
            live_weight REAL,
            rate REAL,
            total REAL
        )
    ''')
    
    # 2. Customer Sales Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            customer_name TEXT,
            item_type TEXT,
            weight REAL,
            rate REAL,
            total REAL,
            payment_method TEXT
        )
    ''')
    
    # 3. Expenses Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            note TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

st.title("🐔 Blue Bird Farm - Accounting System")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🚚 1. Vendor Purchase", 
    "🛒 2. Customer Sale", 
    "💸 3. Daily Expenses", 
    "📈 4. Profit & Loss Report"
])

# ---------------------------------------------------------
# TAB 1: VENDOR PURCHASE
# ---------------------------------------------------------
with tab1:
    st.header("🚚 Vendor Live Chicken Purchase")
    col1, col2 = st.columns(2)
    
    with col1:
        vendor_name = st.text_input("Vendor Name", placeholder="e.g. John Poultry")
        live_weight_in = st.number_input("Total Live Weight Bought (Kg)", min_value=0.1, value=50.0, step=1.0)
    
    with col2:
        buy_rate = st.number_input("Purchase Rate per Kg (Rs)", min_value=1.0, value=180.0, step=5.0)
        purchase_total = live_weight_in * buy_rate
        st.subheader(f"Total Purchase Cost: Rs. {purchase_total:.2f}")

    if st.button("Save Purchase Entry", use_container_width=True):
        if vendor_name.strip() == "":
            st.error("Please enter Vendor Name!")
        else:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO purchases (date, vendor_name, live_weight, rate, total) VALUES (date('now'), ?, ?, ?, ?)",
                      (vendor_name, live_weight_in, buy_rate, purchase_total))
            conn.commit()
            conn.close()
            st.success(f"Successfully recorded purchase from {vendor_name}! 🎉")

# ---------------------------------------------------------
# TAB 2: CUSTOMER SALE & SKINLESS CONVERSION
# ---------------------------------------------------------
with tab2:
    st.header("🛒 Customer Sale & Processing")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        customer_name = st.text_input("Customer Name", value="Cash Customer")
        sale_type = st.selectbox("Sale Type", ["Skinless Chicken", "Live Chicken", "Parts / Eggs"])
        
        if sale_type == "Skinless Chicken":
            live_wt = st.number_input("Initial Live Weight (Kg)", min_value=0.1, value=2.0, step=0.1)
            default_cleaned = round(live_wt * 0.70, 2)
            final_weight = st.number_input("Final Skinless Weight (Kg)", min_value=0.05, value=default_cleaned, step=0.05)
            st.caption(f"💡 Cleaning Weight Loss: {round(live_wt - final_weight, 2)} Kg")
        else:
            final_weight = st.number_input("Weight (Kg)", min_value=0.1, value=2.0, step=0.1)

    with col_s2:
        sell_rate = st.number_input("Selling Rate per Kg (Rs)", min_value=1.0, value=260.0, step=5.0)
        sale_total = final_weight * sell_rate
        st.subheader(f"Total Bill: Rs. {sale_total:.2f}")
        payment_method = st.radio("Payment Method", ["Cash", "Online/Bank Transfer", "Credit (Kadan)"])

    if st.button("Save Sale Bill", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO sales (date, customer_name, item_type, weight, rate, total, payment_method) VALUES (date('now'), ?, ?, ?, ?, ?, ?)",
                  (customer_name, sale_type, final_weight, sell_rate, sale_total, payment_method))
        conn.commit()
        conn.close()
        st.success(f"Bill Saved for {customer_name}! Total: Rs.{sale_total:.2f} 🎉")

# ---------------------------------------------------------
# TAB 3: DAILY EXPENSES
# ---------------------------------------------------------
with tab3:
    st.header("💸 Add Business Expenses")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        exp_category = st.selectbox("Expense Category", ["Transport / Fuel", "Shop Rent", "Electricity / Water", "Salary / Labor", "Feed / Bags", "Other Expenses"])
        exp_amount = st.number_input("Amount Paid (Rs)", min_value=1.0, value=100.0, step=10.0)
        
    with col_e2:
        exp_note = st.text_input("Note / Details", placeholder="e.g. Van transport charge")

    if st.button("Save Expense", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO expenses (date, category, amount, note) VALUES (date('now'), ?, ?, ?)",
                  (exp_category, exp_amount, exp_note))
        conn.commit()
        conn.close()
        st.success("Expense recorded successfully! 💸")

# ---------------------------------------------------------
# TAB 4: PROFIT & LOSS REPORT
# ---------------------------------------------------------
with tab4:
    st.header("📈 Overall Profit & Loss Summary")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Total Sales
    c.execute("SELECT SUM(total) FROM sales")
    total_sales = c.fetchone()[0] or 0.0
    
    # Total Purchases
    c.execute("SELECT SUM(total) FROM purchases")
    total_purchases = c.fetchone()[0] or 0.0
    
    # Total Expenses
    c.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = c.fetchone()[0] or 0.0
    
    conn.close()
    
    # Net Profit
    net_profit = total_sales - (total_purchases + total_expenses)
    
    # Metrics Display
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🛒 Total Sales", f"Rs. {total_sales:.2f}")
    m2.metric("🚚 Total Purchases", f"Rs. {total_purchases:.2f}")
    m3.metric("💸 Total Expenses", f"Rs. {total_expenses:.2f}")
    
    if net_profit >= 0:
        m4.metric("🎉 Net Profit", f"Rs. {net_profit:.2f}", delta=f"+Rs.{net_profit:.2f}")
    else:
        m4.metric("⚠️ Net Loss", f"Rs. {net_profit:.2f}", delta=f"Rs.{net_profit:.2f}")
        
    st.markdown("---")
    st.subheader("📜 Transaction Records")
    
    show_table = st.radio("View Records For:", ["Sales History", "Purchase History", "Expense History"])
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if show_table == "Sales History":
        c.execute("SELECT date, customer_name, item_type, weight, rate, total, payment_method FROM sales ORDER BY id DESC")
        st.dataframe(c.fetchall(), use_container_width=True)
    elif show_table == "Purchase History":
        c.execute("SELECT date, vendor_name, live_weight, rate, total FROM purchases ORDER BY id DESC")
        st.dataframe(c.fetchall(), use_container_width=True)
    else:
        c.execute("SELECT date, category, amount, note FROM expenses ORDER BY id DESC")
        st.dataframe(c.fetchall(), use_container_width=True)
        
    conn.close()
