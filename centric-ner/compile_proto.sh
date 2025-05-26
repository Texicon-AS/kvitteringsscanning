#!/bin/bash

# Make sure the required tools are installed
if ! command -v python3 -m pip &> /dev/null
then
    echo "Python pip is not installed. Installing..."
    python3 -m ensurepip --upgrade
fi

# Install required packages if not already installed
pip install grpcio grpcio-tools

# Compile the proto file
python3 -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  ./src/api/proto/ner.proto

echo "Proto file compiled successfully!" 