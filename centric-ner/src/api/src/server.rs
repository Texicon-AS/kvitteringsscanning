mod client;

use std::io::{BufRead, BufReader, Write};
use std::path::Path;
use std::process::{Child, Command};
use std::sync::{Arc, Mutex};
use tonic::{transport::Server, Request, Response, Status};

use ner::prediction_server::{Prediction, PredictionServer};
use ner::{PredictedDataReply, ReceiptDataRequest};

pub mod ner {
    tonic::include_proto!("ner");
}

#[derive(Debug)]
struct PythonProcess {
    child: Child,
    stdin: std::process::ChildStdin,
    stdout_reader: BufReader<std::process::ChildStdout>,
}
#[derive(Debug)]
pub struct MyPrediction {
    python_process: Option<PythonProcess>,
}

impl Default for MyPrediction {
    fn default() -> Self {
        Self {
            python_process: None,
        }
    }
}
impl MyPrediction {
    fn new() -> Self {
        Self {
            python_process: None,
        }
    }
    fn start(&mut self) -> Result<(), String> {
        println!("Starting python process");
        if self.python_process.is_none() {
            let cd = std::env::current_dir().expect("Failed to get current dir");
            let parent = cd
                .parent()
                .and_then(|p| p.parent())
                .unwrap_or_else(|| { &*cd }); // in docker image, the server is at the top directory, and the layout is different, there's no need to go up.
            let src_path = Path::join(&parent, "src");
            let path = Path::join(&src_path, "main.py");
            let mut child = Command::new("python")
                .arg(&path)
                .arg("-s")
                .arg("-m")
                .arg(parent)
                .stdin(std::process::Stdio::piped())
                .stdout(std::process::Stdio::piped())
                .stderr(std::process::Stdio::inherit())
                .env_clear()
                .envs(std::env::vars())
                .spawn()
                .map_err(|e| {
                    format!(
                        "Failed to spawn python process: {} {}",
                        e,
                        &parent.display()
                    )
                })?;

            let stdin = child.stdin.take().ok_or("Failed to get stdin handle")?;
            let stdout = child.stdout.take().ok_or("Failed to get stdout handle")?;

            let stdout_reader = BufReader::new(stdout);

            self.python_process = Some(PythonProcess {
                child,
                stdout_reader,
                stdin,
            });
        }

        Ok(())
    }

    fn send_to_python(&mut self, command: &str) -> Result<String, String> {
        self.start()?;
        println!("Sending to python string: {}", command);
        if let Some(process) = &mut self.python_process {
            let command_to_send = if command.ends_with('\n') {
                command.to_string()
            } else {
                format!("{}\n", command)
            };

            process
                .stdin
                .write_all(&command_to_send.as_bytes())
                .map_err(|e| format!("Failed to send command : {}", e))?;

            println!("Sent to python stdin");
            process
                .stdin
                .flush()
                .map_err(|e| format!("Failed to flush stdin: {}", e))?;
            println!("Flushed stdin");
            let mut output = String::new();
            process
                .stdout_reader
                .read_line(&mut output)
                .map_err(|e| format!("Failed to read stdout: {}", e))?;
            println!("Read stdout");
            Ok(output.trim().to_string())
        } else {
            Err(format!("Failed to spawn python program: {}", command))
        }
    }
}

impl Drop for MyPrediction {
    fn drop(&mut self) {
        if let Some(python_process) = &mut self.python_process.take() {
            let _ = python_process.child.kill();
            let _ = python_process.child.wait();
        }
    }
}

#[tonic::async_trait]
impl Prediction for Arc<Mutex<MyPrediction>> {
    // TODO! makes this take in stdin instead of calling model again and again.
    async fn predict(
        &self,
        request: Request<ReceiptDataRequest>,
    ) -> Result<Response<PredictedDataReply>, Status> {
        println!("Starting prediction");
        let commands = request.into_inner();
        let service = Arc::clone(self);

        let output = tokio::task::spawn_blocking(move || {
            let mut ingredients = Vec::new();
            let mut service = match service.lock() {
                Ok(guard) => guard,
                Err(_) => return vec![ ner::IngredientData{
                    ingredient :"Mutex lock poisoned".to_string(),
                    quantity : String::new(),
                    groups : String::new(),
                } ],
            };
            for command in commands.items {
                match service.send_to_python(&command) {
                    Ok(output) => {
                        println!("{}", &output);
                        // Parse the fixed format: "Ingredient: {i} | Groups: {j} | Quantity: {k}"
                        let mut ingredient_name = String::new();
                        let mut groups = String::new();
                        let mut quantity = String::new();

                        if let Some(i_start) = output.find("Ingredient: ") {
                            let i_start = i_start + "Ingredient: ".len();
                            if let Some(i_end) = output[i_start..].find(" | ") {
                                ingredient_name = output[i_start..(i_start+i_end)].trim().to_string();
                            }
                        }

                        if let Some(g_start) = output.find("Groups: ") {
                            let g_start = g_start + "Groups: ".len();
                            if let Some(g_end) = output[g_start..].find(" | ") {
                                groups = output[g_start..(g_start + g_end)].trim().to_string();
                            }
                        }

                        if let Some(q_start) = output.find("Quantity: ") {
                            let q_start = q_start + "Quantity: ".len();
                            quantity = output[q_start..].trim().to_string();
                        }

                        let ingredient_data = ner::IngredientData {
                            ingredient : ingredient_name,
                            quantity : quantity,
                            groups : groups,
                        };

                        ingredients.push(ingredient_data);
                    }
                    Err(e) => {
                        let ingredient_data = ner::IngredientData {
                            ingredient: format!("Error: {}", e),
                            quantity: String::new(),
                            groups: String::new(),
                        };
                        ingredients.push(ingredient_data);
                    },
                }
            }
            ingredients
        })
        .await
        .map_err(|e| Status::internal(format!("Failed to execute task: {}", e)));

        let result = PredictedDataReply { ingredients : output? };
        Ok(Response::new(result))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Server starting!");
    let addr = "0.0.0.0:50051".parse()?;
    // let prediction = MyPrediction::new();
    let prediction = Arc::new(Mutex::new(MyPrediction::new()));
    println!("Predictions started!");
    Server::builder()
        .add_service(PredictionServer::new(prediction))
        .serve(addr)
        .await?;

    Ok(())
}
