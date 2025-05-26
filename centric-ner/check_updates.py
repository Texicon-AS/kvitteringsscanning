import psycopg2

# Database connection parameters
DB_URI = "postgresql://postgres:xPDzXdllaEyZlpukUwCFBujFuvGinVON@junction.proxy.rlwy.net:50523/railway"

def main():
    # Connect to database
    print("Connecting to database...")
    conn = psycopg2.connect(DB_URI)
    
    try:
        cursor = conn.cursor()
        
        # Sample of updated products
        cursor.execute("""
            SELECT id, name, bulk_product_amount, unit 
            FROM product 
            WHERE bulk_product_amount IS NOT NULL 
            AND bulk_product_amount <> 0
            LIMIT 20
        """)
        
        print("\nSample of products with updated quantities:")
        print("ID | Name | Amount | Unit")
        print("-" * 80)
        
        for row in cursor.fetchall():
            product_id, name, amount, unit = row
            print(f"{product_id} | {name} | {amount} | {unit}")
        
        # Count of updated products
        cursor.execute("""
            SELECT COUNT(*) 
            FROM product 
            WHERE bulk_product_amount IS NOT NULL 
            AND bulk_product_amount <> 0
        """)
        
        updated_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM product
        """)
        
        total_count = cursor.fetchone()[0]
        
        print("\nSummary:")
        print(f"Total products: {total_count}")
        print(f"Products with quantities: {updated_count}")
        print(f"Percentage with quantities: {(updated_count / total_count) * 100:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 