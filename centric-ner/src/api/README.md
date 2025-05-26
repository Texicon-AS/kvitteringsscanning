# TODO:
 - versioning for the api?
 - stdin streaming
 - calling actual predictNER.py

# Prerequisites
Things that you need to install for this to run:
    - Rust [https://www.rust-lang.org/tools/install]
    - protobuf [https://grpc.io/docs/protoc-installation/]

# How to run
Simple client and server files are made for demonstration purposes:
   ### client: (for testing purposes) 
    cargo run --bin ner-client
   ### server
    cargo run --bin ner-server
