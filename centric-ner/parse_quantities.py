import psycopg2
import psycopg2.pool
import csv
import re
import sys
import time
import concurrent.futures
from functools import lru_cache

# Database connection parameters
DB_URI = "postgresql://postgres:xPDzXdllaEyZlpukUwCFBujFuvGinVON@junction.proxy.rlwy.net:50523/railway"

# Units mapping
UNIT_MAPPING = {
    # Gram units
    'g': 'gram',
    'gr': 'gram',
    'gram': 'gram',
    'kg': 'kilogram',
    'kilo': 'kilogram',
    'kilogram': 'kilogram',
    
    # Volume units
    'ml': 'milliliter',
    'milliliter': 'milliliter',
    'cl': 'centiliter',
    'centiliter': 'centiliter',
    'dl': 'deciliter',
    'deciliter': 'deciliter',
    'l': 'liter',
    'liter': 'liter',
    
    # Piece units
    'stk': 'piece',
    'stykk': 'piece',
    'stykker': 'piece',
    'pk': 'piece',
    'pakke': 'piece',
    'pakker': 'piece',
    'x': 'piece'
}

# Create a connection pool
connection_pool = None

@lru_cache(maxsize=1024)
def parse_quantity(quantity_str):
    """
    Parse quantity string to extract amount and unit.
    Returns tuple of (amount, unit)
    Cache results to avoid parsing the same quantity string multiple times.
    """
    if not quantity_str or quantity_str == 'NOT_FOUND':
        return None, None
    
    # Clean the quantity string
    quantity_str = quantity_str.strip().lower()
    
    # Handle format like "0,50l" - common in Scandinavian format
    match = re.search(r'(\d+)[,\.](\d+)([a-zæøå]+)', quantity_str)
    if match:
        whole, decimal, unit = match.groups()
        amount = float(f"{whole}.{decimal}")
        
        # Convert to standard unit
        standard_unit = UNIT_MAPPING.get(unit)
        if standard_unit:
            # Convert to proper units (for liters, we need to handle ml, cl, dl)
            if unit == 'l' and standard_unit == 'liter' and amount < 1:
                if amount <= 0.01:
                    amount = round(amount * 1000, 1)
                    standard_unit = 'milliliter'
                elif amount <= 0.1:
                    amount = round(amount * 100, 1)
                    standard_unit = 'centiliter'
                elif amount < 1:
                    amount = round(amount * 10, 1)
                    standard_unit = 'deciliter'
            
            # Round to 1 decimal place to avoid floating point issues
            amount = round(amount, 1)
            return int(amount) if amount.is_integer() else amount, standard_unit
    
    # Handle special case for X format (e.g. "4 x 125g")
    match = re.search(r'(\d+)\s*x\s*(\d+)(?:\s*|\.)(\d*)\s*([a-zæøå]+)', quantity_str)
    if match:
        count, size1, size2, unit = match.groups()
        size = float(f"{size1}.{size2}" if size2 else size1)
        amount = float(count) * size
        standard_unit = UNIT_MAPPING.get(unit)
        if standard_unit:
            # Round to 1 decimal place to avoid floating point issues
            amount = round(amount, 1)
            return int(amount) if amount.is_integer() else amount, standard_unit
    
    # Try to find a number followed by a unit
    match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zæøå]+)', quantity_str)
    if match:
        amount_str, unit_str = match.groups()
        amount = float(amount_str)
        unit = unit_str.strip()
        
        # Map to standardized unit
        standard_unit = UNIT_MAPPING.get(unit)
        if standard_unit:
            # Round to 1 decimal place to avoid floating point issues
            amount = round(amount, 1)
            return int(amount) if amount.is_integer() else amount, standard_unit
    
    # Extract numbers with potential decimal point
    match = re.search(r'(\d+)(?:\.|\,)(\d+)', quantity_str)
    if match:
        whole, decimal = match.groups()
        amount = float(f"{whole}.{decimal}")
        
        # Try to find unit after the number
        unit_match = re.search(r'(?:\d+(?:\.|\,)\d+)\s*([a-zæøå]+)', quantity_str)
        if unit_match:
            unit = unit_match.group(1)
            standard_unit = UNIT_MAPPING.get(unit)
            if standard_unit:
                # Round to 1 decimal place to avoid floating point issues
                amount = round(amount, 1)
                return int(amount) if amount.is_integer() else amount, standard_unit
        
        # For values like 0.5 or 0.33, likely liters for beverages if no unit specified
        if 0.1 <= amount <= 3.0:
            # Round to 1 decimal place to avoid floating point issues
            amount = round(amount, 1)
            return int(amount) if amount.is_integer() else amount, 'liter'
        
        # Default to piece if no unit found
        # Round to 1 decimal place to avoid floating point issues
        amount = round(amount, 1)
        return int(amount) if amount.is_integer() else amount, 'piece'
    
    # Extract just numbers if no unit is found
    match = re.search(r'(\d+)', quantity_str)
    if match:
        amount = float(match.group(1))
        # For values between 20 and 750, likely milliliters or grams
        if 20 <= amount <= 750:
            # Heuristic: odd numbers tend to be grams, round numbers tend to be milliliters
            if amount % 5 != 0:
                return int(amount), 'gram'
            else:
                return int(amount), 'milliliter'
        # For values between 1 and 10, likely pieces or kilograms
        elif 1 <= amount <= 10:
            return int(amount), 'piece'
        else:
            return int(amount), 'piece'  # Default to piece if no unit specified
    
    return None, None

def load_csv_data(csv_file):
    """Load CSV data into a dictionary with product name as key."""
    products_data = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_name = row['product_name']
            if product_name and product_name not in products_data:
                products_data[product_name] = row
    return products_data

def get_connection():
    """Get a connection from the pool."""
    global connection_pool
    return connection_pool.getconn()

def return_connection(conn):
    """Return a connection to the pool."""
    global connection_pool
    connection_pool.putconn(conn)

def get_valid_units():
    """Get valid unit values from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT slug FROM enum_product_unit")
        valid_units = {row[0] for row in cursor.fetchall()}
        cursor.close()
        return valid_units
    finally:
        return_connection(conn)

def get_products_with_zero_amount(limit=None):
    """Get all products with bulk_product_amount = 0 or NULL."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Optimize query with proper indexing hint
        query = """
            SELECT id, name
            FROM product
            WHERE (bulk_product_amount IS NULL OR bulk_product_amount = 0)
            ORDER BY id
        """
        
        if limit:
            query += f" LIMIT {limit}"
            
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results
    finally:
        return_connection(conn)

def process_product(product_data, valid_units, csv_data, dry_run, test_mode):
    """Process a single product and update it if possible."""
    product_id, product_name = product_data
    result = {
        'updated': False,
        'failed': False,
        'not_found': False,
        'no_quantity': False,
        'log': ''
    }
    
    if product_name in csv_data:
        quantity_str = csv_data[product_name]['quantity']
        amount, unit = parse_quantity(quantity_str)
        
        if amount is not None and unit is not None and unit in valid_units:
            if test_mode:
                result['log'] = f"Processing: {product_name} - {quantity_str} -> {amount} {unit}"
            
            if not dry_run:
                conn = get_connection()
                try:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE product
                            SET bulk_product_amount = %s, unit = %s
                            WHERE id = %s
                        """, (amount * 100, unit, product_id))
                        conn.commit()
                        result['updated'] = True
                    except Exception as e:
                        conn.rollback()
                        result['log'] += f"\nError updating product {product_id}: {e}"
                        result['failed'] = True
                    finally:
                        cursor.close()
                finally:
                    return_connection(conn)
            else:
                if test_mode:
                    result['log'] += f"\n  [DRY RUN] Would update product {product_id} with amount={amount}, unit={unit}"
                result['updated'] = True
        else:
            if test_mode:
                result['log'] = f"Skipping {product_name}: invalid quantity '{quantity_str}' or unit '{unit}'"
            result['no_quantity'] = True
    else:
        result['not_found'] = True
        if test_mode:
            result['log'] = f"Not found in CSV: {product_name}"
    
    return result

def initialize_connection_pool(min_conn=2, max_conn=10):
    """Initialize the connection pool."""
    global connection_pool
    connection_pool = psycopg2.pool.ThreadedConnectionPool(min_conn, max_conn, DB_URI)

def main():
    start_time = time.time()
    
    # Parse command line arguments
    test_mode = "--test" in sys.argv
    dry_run = "--dry-run" in sys.argv
    
    # Look for limit parameter
    limit = None
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
                break
            except ValueError:
                pass
    
    # Look for threads parameter
    max_workers = 4  # Default number of workers
    for i, arg in enumerate(sys.argv):
        if arg == "--threads" and i + 1 < len(sys.argv):
            try:
                max_workers = int(sys.argv[i + 1])
                break
            except ValueError:
                pass
    
    # Default to 10 for test mode if no explicit limit given
    if test_mode and limit is None:
        limit = 10
        
    if test_mode:
        print(f"Running in TEST mode with limit of {limit} products")
    if dry_run:
        print("Running in DRY RUN mode - no database changes will be made")
    if limit and not test_mode:
        print(f"Processing with limit of {limit} products")
    print(f"Using {max_workers} worker threads")
    
    # Load CSV data
    print("Loading CSV data...")
    csv_data = load_csv_data('output.csv')
    print(f"Loaded {len(csv_data)} products from CSV")
    
    # Initialize connection pool
    print("Initializing database connection pool...")
    initialize_connection_pool(min_conn=2, max_conn=max_workers + 2)
    
    try:
        # Get valid units from database
        valid_units = get_valid_units()
        print(f"Valid units in database: {', '.join(valid_units)}")
        
        # Get products with zero amount
        print("Getting products with zero amount...")
        products = get_products_with_zero_amount(limit)
        print(f"Found {len(products)} products with zero amount")
        
        # Counters for stats
        updated_count = 0
        failed_count = 0
        not_found_count = 0
        no_quantity_count = 0
        
        # Process products in parallel
        batch_size = 100
        total_batches = (len(products) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            batch_start = batch_num * batch_size
            batch_end = min((batch_num + 1) * batch_size, len(products))
            batch = products[batch_start:batch_end]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(process_product, product, valid_units, csv_data, dry_run, test_mode)
                    for product in batch
                ]
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result['log']:
                        print(result['log'])
                    
                    if result['updated']:
                        updated_count += 1
                    if result['failed']:
                        failed_count += 1
                    if result['not_found']:
                        not_found_count += 1
                    if result['no_quantity']:
                        no_quantity_count += 1
            
            # Print progress after each batch
            elapsed = time.time() - start_time
            products_processed = batch_end
            print(f"Processed {products_processed}/{len(products)} products in {elapsed:.2f} seconds ({products_processed/elapsed:.2f} products/sec)")
        
        elapsed_time = time.time() - start_time
        
        print("\nSummary:")
        print(f"Updated: {updated_count} products")
        print(f"Failed: {failed_count} products")
        print(f"Not found in CSV: {not_found_count} products")
        print(f"Invalid/missing quantity: {no_quantity_count} products")
        print(f"Total products processed: {len(products)}")
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"Average processing speed: {len(products)/elapsed_time:.2f} products/second")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close all connections in the pool
        if connection_pool:
            connection_pool.closeall()

if __name__ == "__main__":
    main() 