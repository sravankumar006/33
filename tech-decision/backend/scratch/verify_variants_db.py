import os
import sys
import sqlite3

def verify():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tech_decision.db")
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check phone_variants table
    cursor.execute("SELECT count(*) FROM phone_variants;")
    variants_count = cursor.fetchone()[0]
    print(f"Total variants in phone_variants: {variants_count}")
    
    # Check variant_prices table
    cursor.execute("SELECT count(*) FROM variant_prices;")
    prices_count = cursor.fetchone()[0]
    print(f"Total prices in variant_prices: {prices_count}")
    
    # Show some sample variants
    print("\nSample variants:")
    cursor.execute("SELECT pv.id, p.brand, p.model, pv.ram_gb, pv.storage_gb, pv.color, pv.slug FROM phone_variants pv JOIN phones p ON pv.phone_id = p.id LIMIT 5;")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Device: {row[1]} {row[2]} | {row[3]}GB RAM | {row[4]}GB Storage | Color: {row[5]} | Slug: {row[6]}")
        
    # Show some sample variant prices
    print("\nSample variant prices:")
    cursor.execute("""
        SELECT vp.id, pv.slug, vp.platform, vp.listed_price, vp.delivery_charge, vp.final_price 
        FROM variant_prices vp 
        JOIN phone_variants pv ON vp.variant_id = pv.id 
        LIMIT 5;
    """)
    for row in cursor.fetchall():
        print(f"Price ID: {row[0]} | Variant: {row[1]} | Plat: {row[2]} | Listed Price: {row[3]} | Delivery: {row[4]} | Final Price: {row[5]}")
        
    conn.close()

if __name__ == "__main__":
    verify()
