# Product Ingredient Extractor

This script extracts product names from a PostgreSQL database and queries a gRPC service to predict ingredients for each product.

## Prerequisites

- Python 3.6+
- PostgreSQL connection
- gRPC service running at localhost:50051

## Setup

1. Install required packages:

   ```
   pip install psycopg2-binary grpcio grpcio-tools
   ```

2. Compile the gRPC proto file:

   ```
   chmod +x compile_proto.sh
   ./compile_proto.sh
   ```

   This will create the necessary Python modules:

   - `predict_pb2.py`
   - `predict_pb2_grpc.py`

## Usage

1. Make sure your gRPC service is running at `localhost:50051`

2. Run the script:

   ```
   python tradesolution_to_ingredients.py
   ```

3. The script will:
   - Query all product names from the database
   - Send each product name to the gRPC service
   - Write the results to `output.csv`

## Output Format

The `output.csv` file contains the following columns:

- `product_name`: The name of the product from the database
- `ingredient_name`: The name of the ingredient
- `quantity`: The quantity of the ingredient
- `groups`: The groups the ingredient belongs to
