import psycopg2
import csv
import grpc
import json
from google.protobuf.json_format import MessageToDict
import os
import sys

# Add the correct path to the generated gRPC modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the generated gRPC modules
try:
    import src.api.proto.ner_pb2
    import src.api.proto.ner_pb2_grpc
except ImportError:
    print("Error: Could not import the gRPC proto modules.")
    print("Make sure the proto files are compiled and in the correct path.")
    sys.exit(1)

# Database connection parameters
DB_URI = "postgresql://postgres:xPDzXdllaEyZlpukUwCFBujFuvGinVON@junction.proxy.rlwy.net:50523/railway"

# gRPC service details
GRPC_SERVER = "localhost:50051"

def get_product_names():
    """Query all product names from the database."""
    try:
        conn = psycopg2.connect(DB_URI)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM product")
        product_names = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return product_names
    except Exception as e:
        print(f"Database error: {e}")
        return []

def predict_ingredients(product_name):
    """Send product name to gRPC service and get predicted ingredients."""
    try:
        channel = grpc.insecure_channel(GRPC_SERVER)
        stub = src.api.proto.ner_pb2_grpc.PredictionStub(channel)
        
        # Create request message
        request = src.api.proto.ner_pb2.ReceiptDataRequest(items=[product_name])
        
        # Make gRPC call
        response = stub.predict(request)
        
        # Convert response to dictionary
        response_dict = MessageToDict(response)
        
        return response_dict.get('ingredients', [])
    except Exception as e:
        print(f"gRPC error for '{product_name}': {e}")
        return []

def main():
    # Get all product names from database
    print("Fetching product names from database...")
    product_names = get_product_names()
    print(f"Found {len(product_names)} products")
    
    # Prepare CSV file
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_name', 'ingredient_name', 'quantity', 'groups']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each product
        for i, product_name in enumerate(product_names):
            if i % 10 == 0:
                print(f"Processing product {i+1}/{len(product_names)}")
            
            ingredients = predict_ingredients(product_name)
            
            # Write each ingredient to CSV
            for ingredient in ingredients:
                writer.writerow({
                    'product_name': product_name,
                    'ingredient_name': ingredient.get('ingredient', ''),
                    'quantity': ingredient.get('quantity', ''),
                    'groups': ingredient.get('groups', '')
                })
    p
    print(f"Results saved to output.csv")

if __name__ == "__main__":
    main()
