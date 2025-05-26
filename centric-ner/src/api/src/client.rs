use crate::ner::prediction_client::PredictionClient;
use crate::ner::ReceiptDataRequest;

pub mod ner {
    tonic::include_proto!("ner");
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = match PredictionClient::connect("http://127.0.0.1:50052").await {
        Ok(client) => client,
        Err(e) => {
            eprintln!("Failed to connect: {:?}",e);
            return Err(e.into());
        },
    };

    // In client.rs
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await; // Wait for server to start
    println!("client connected " );
    let request = tonic::Request::new(ReceiptDataRequest {
        items: vec![
            "Norvegia ca. 500g".into(),
        ],
    });

    let result =match
    client.predict(request).await
    {
        Ok(result) => result.into_inner(),
        Err(e) => panic!("PANIC at predicting {}", e),
    };

    println!("RESPONSE={:?}", result);

    Ok(())
}
