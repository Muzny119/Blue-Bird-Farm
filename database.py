import sqlite3

def init_db():
    conn = sqlite3.connect("poultry_shop.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            item_name TEXT,
            weight_kg REAL,
            price_per_kg REAL,
            total_amount REAL,
            payment_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database Created!")
