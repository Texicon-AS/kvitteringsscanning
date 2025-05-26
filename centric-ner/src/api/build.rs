
// Build step to compile protobufs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("proto/ner.proto")?;
    Ok(())
}
