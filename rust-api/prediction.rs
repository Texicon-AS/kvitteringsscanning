use tonic::transport::Channel;

use crate::proto::ner::prediction_client::PredictionClient as GrpcClient;

const RETRY_SLEEP_DUR: tokio::time::Duration = tokio::time::Duration::from_secs(2);
const TEST_PRODUCT: &str = "Testeprodukt 100g";

#[derive(Clone)]
pub struct Client {
    inner: GrpcClient<Channel>,
}

impl Client {
    pub async fn predict(&mut self, items: Vec<String>) -> Result<Vec<Option<Output>>, ()> {
        let request = crate::proto::ner::ReceiptDataRequest { items };
        let response = self.inner.predict(request).await;

        match response {
            Ok(r) => Ok(r
                .into_inner()
                .ingredients
                .into_iter()
                .map(Output::from_response)
                .collect()),
            Err(_) => Err(()),
        }
    }
}

pub struct Output {
    pub name: String,
    pub ingredient_categories: Vec<String>,
    pub amount: Amount,
}

impl Output {
    fn from_response(value: crate::proto::ner::IngredientData) -> Option<Self> {
        log::info!("Prediction: {:?}", &value);

        if value.ingredient == "NOT_FOUND" {
            return None;
        }

        let mut groups = value.groups;

        if groups.starts_with('[') {
            groups.remove(0);
        }
        if groups.ends_with(']') {
            groups.pop();
        }

        let ingredient_categories = groups.split(", ").map(ToOwned::to_owned).collect();

        let amount = to_unit_quantity(&value.quantity);

        Some(Self {
            name: value.ingredient,
            ingredient_categories,
            amount,
        })
    }
}

pub struct Amount {
    pub quantity: Option<u32>,
    pub unit: Option<String>,
}

fn to_unit_quantity(prediction_output: &str) -> Amount {
    let quantity = prediction_output.replace(|c: char| !c.is_ascii_digit(), "");
    let quantity = quantity.parse().ok().map(|q: u32| q * 100);

    let out = Amount {
        quantity,
        unit: None,
    };

    let unit = prediction_output.replace(|c: char| c.is_ascii_digit(), "");
    let lowercased = unit.to_lowercase();

    let (magnitude, unit) = match &lowercased[..] {
        "g" => (1, "gram"),
        "stk" => (1, "piece"),
        "ml" => (1, "milliliter"),
        "dl" => (100, "milliliter"),
        "l" => (1000, "milliliter"),
        "not_found" => return out,
        other => {
            log::warn!(r#"Unsupported unit from ingredient predictor: "{other}""#);
            return out;
        }
    };

    Amount {
        quantity: out.quantity.map(|q| q * magnitude),
        unit: Some(unit.to_owned()),
    }
}

#[derive(Debug)]
pub struct CouldNotConnect;

impl std::fmt::Display for CouldNotConnect {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Client could not connect to the ingredient prediction server. Is the server running?"
        )
    }
}

impl std::error::Error for CouldNotConnect {}

pub async fn client() -> Result<Client, CouldNotConnect> {
    let url = std::env::var("CENTRIC_URL").unwrap();
    log::info!("Predictor URL: {}", &url);

    let mut tries = 0;
    let mut inner = loop {
        tries += 1;
        match GrpcClient::connect(url.clone()).await {
            Ok(inner) => break inner,
            Err(e) if tries > 3 => {
                log::error!("{e}; {e:?}");
                return Err(CouldNotConnect);
            }
            _ => tokio::time::sleep(RETRY_SLEEP_DUR).await,
        };
    };

    let test_request = crate::proto::ner::ReceiptDataRequest {
        items: vec![TEST_PRODUCT.to_owned()],
    };

    inner
        .predict(test_request)
        .await
        .map_err(|_| CouldNotConnect)?;

    Ok(Client { inner })
}
