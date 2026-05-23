import sqlite3

def main():
    conn = sqlite3.connect("tech_decision.db")
    cursor = conn.cursor()
    
    # Drop phone_variants and variant_prices if they exist
    print("Dropping tables...")
    cursor.execute("DROP TABLE IF EXISTS variant_prices;")
    cursor.execute("DROP TABLE IF EXISTS phone_variants;")
    
    conn.commit()
    print("Tables dropped successfully.")
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    print("Tables in DB now:", tables)
    
    conn.close()

if __name__ == "__main__":
    main()
