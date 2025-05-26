## Compile rust API
FROM rust:latest AS builder

WORKDIR /app

RUN apt-get update && apt-get -y install protobuf-compiler
COPY /src/api .
RUN cargo build --release


# Final Stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/target/release/ .

## Download spaCy package
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY /src/ /app/src/
COPY /sample_data /app/sample_data/

## entrypoint for rust API.
CMD ["./ner-server"]
