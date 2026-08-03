import sqlite3
import streamlit as st

st.set_page_config(page_title="Blue Bird Farm - Accounting", page_icon="🐔", layout="wide")

DB_FILE = 'farm_v3.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Vendor Live Purchases
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
    
    # 2. Skinless Processing Logs (Batch Processing)
    c.execute('''
        CREATE TABLE IF NOT EXISTS processing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            live_weight_used REAL,
            skinless_weight_produced REAL,
            waste_loss REAL
        )
    ''')
    
    # 3. Customer Sales
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
    
    # 4. Expenses
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

st.title("🐔 Blue Bird Farm - Accounting & Inventory")

# 4 Sequential Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚚 1. Vendor Purchase", 
    "🔪 2. Skinless Conversion", 
    "🛒 3. Customer Sale", 
    "💸 4. Daily Expenses", 
    "📈 5. Profit & Loss"
])

# ---------------------------------------------------------
# TAB 1: VENDOR LIVE PURCHASE
# ---------------------------------------------------------
with tab1:
    st.header("🚚 Step 1: Buy Live Chicken from Vendor")
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
            st.success(f"Saved Live Purchase from {vendor_name}! 🎉")

# ---------------------------------------------------------
# TAB 2: SKINLESS PROCESSING CONVERSION
# ---------------------------------------------------------
with tab2:
    st.header("🔪 Step 2: Convert Live Chicken to Skinless")
    st.caption("Record live weight cleaned today and exact skinless yield obtained.")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        live_used = st.number_input("Live Weight Taken for Cleaning (Kg)", min_value=0.1, value=10.0, step=0.5)
        # Standard approx 70% yield
        default_skinless = round(live_used * 0.70, 2)
        skinless_produced = st.number_input("Actual Skinless Chicken Obtained (Kg)", min_value=0.1, value=default_skinless, step=0.1)
    
    with col_p2:
        waste_loss = round(live_used - skinless_produced, 2)
        st.markdown(f"### ⚖️ Cleaning Loss / Waste: **{waste_loss} Kg**")
        if live_used > 0:
            yield_pct = round((skinless_produced / live_used) * 100, 1)
            st.info(f"Yield Efficiency: **{yield_pct}%** Skinless output")

    if st.button("Save Processing Record", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO processing (date, live_weight_used, skinless_weight_produced, waste_loss) VALUES (date('now'), ?, ?, ?)",
                  (live_used, skinless_produced, waste_loss))
        conn.commit()
        conn.close()
        st.success("Skinless processing entry recorded successfully! 🎉")

# ---------------------------------------------------------
# TAB 3: CUSTOMER SALE
# ---------------------------------------------------------
with tab3:
    st.header("🛒 Step 3: Sell Processed Chicken to Customer")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        customer_name = st.text_input("Customer Name", value="Cash Customer")
        sale_type = st.selectbox("Item Sold", ["Skinless Chicken", "Live Chicken", "Chicken Parts / Other"])
        sell_weight = st.number_input("Weight Sold (Kg)", min_value=0.1, value=1.0, step=0.1)

    with col_s2:
        sell_rate = st.number_input("Selling Rate per Kg (Rs)", min_value=1.0, value=260.0, step=5.0)
        sale_total = sell_weight * sell_rate
        st.subheader(f"Total Bill: Rs. {sale_total:.2f}")
        payment_method = st.radio("Payment Method", ["Cash", "Online/Bank Transfer", "Credit (Kadan)"])

    if st.button("Save Customer Sale Bill", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO sales (date, customer_name, item_type, weight, rate, total, payment_method) VALUES (date('now'), ?, ?, ?, ?, ?, ?)",
                  (customer_name, sale_type, sell_weight, sell_rate, sale_total, payment_method))
        conn.commit()
        conn.close()
        st.success(f"Sale recorded for {customer_name}! Total: Rs.{sale_total:.2f} 🎉")

# ---------------------------------------------------------
# TAB 4: DAILY EXPENSES
# ---------------------------------------------------------
with tab4:
    st.header("💸 Step 4: Record Daily Shop Expenses")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        exp_category = st.selectbox("Expense Category", ["Transport / Fuel", "Shop Rent", "Electricity / Water", "Salary / Labor", "Feed / Bags", "Other Expenses"])
        exp_amount = st.number_input("Amount Paid (Rs)", min_value=1.0, value=100.0, step=10.0)
        
    with col_e2:
        exp_note = st.text_input("Note / Details", placeholder="e.g. Transport van fuel")

    if st.button("Save Expense Entry", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO expenses (date, category, amount, note) VALUES (date('now'), ?, ?, ?)",
                  (exp_category, exp_amount, exp_note))
        conn.commit()
        conn.close()
        st.success("Expense recorded successfully! 💸")

# ---------------------------------------------------------
# TAB 5: PROFIT & LOSS REPORT
# ---------------------------------------------------------
with tab5:
    st.header("📈 Step 5: Profit & Loss & Processing Summary")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Financial Aggregates
    c.execute("SELECT SUM(total) FROM sales")
    total_sales = c.fetchone()[0] or 0.0
    
    c.execute("SELECT SUM(total) FROM purchases")
    total_purchases = c.fetchone()[0] or 0.0
    
    c.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = c.fetchone()[0] or 0.0
    
    # Processing Aggregates
    c.execute("SELECT SUM(live_weight_used), SUM(skinless_weight_produced), SUM(waste_loss) FROM processing")
    proc_summary = c.fetchone()
    total_live_proc = proc_summary[0] or 0.0
    total_skinless_obtained = proc_summary[1] or 0.0
    total_waste_loss = proc_summary[2] or 0.0
    
    conn.close()
    
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
    st.subheader("🔪 Skinless Processing Summary")
    p1, p2, p3 = st.columns(3)
    p1.metric("🐔 Total Live Chicken Cleaned", f"{total_live_proc} Kg")
    p2.metric("🥩 Total Skinless Obtained", f"{total_skinless_obtained} Kg")
    p3.metric("🗑️ Total Cleaning Loss", f"{total_waste_loss} Kg")
    
    st.markdown("---")
    st.subheader("📜 Detailed Records")
    
    show_table = st.radio("View History For:", ["Sales History", "Skinless Processing Logs", "Vendor Purchase History", "Expense History"])
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if show_table == "Sales History":
        c.execute("SELECT date, customer_name, item_type, weight, rate, total, payment_method FROM sales ORDER BY id DESC")
        st.dataframe(c.fetchall(), use_container_width=True)
    elif show_table == "Skinless Processing Logs":
        c.execute("SELECT date, live_weight_used, skinless_weight_produced, waste_loss FROM processing ORDER BY id DESC")
        st.dataframe(c.fetchall(), use_container_width=True)
    elif show_table == "Vendor Purchase History":
        c.execute("SELECT date, vendor_name, live_weight, rate, total FROM purchases ORDER BY id DESC")
        st.dataframe(c.fetchall(), use_container_width=True)
    else:
        c.execute("SELECT date, category, amount, note FROM expenses ORDER BY id DESC")
        st.dataframe(c.fetchall(), use_container_width=True)
        
    conn.close()
