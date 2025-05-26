use std::fs::File;
use std::io::ErrorKind;

//The rust error handling boils down to Result type and various functions handling them.
enum Result<T, E> {
    Ok(T),
    Err(E),
}


fn func1() {
    let greeting_file_result = File::open("hello.txt");

    let greeting_file = match greeting_file_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {error:?}"), // macro for stopping program in case of error.
    };
}


fn func2() {
    //unwrap_or_else makes greeting file OK(value) and we only need to handle errors.
    let greeting_file = File::open("hello.txt").unwrap_or_else(|error| { 
        if error.kind() == ErrorKind::NotFound {
            File::create("hello.txt").unwrap_or_else(|error| {
                panic!("Problem creating the file: {error:?}");
            })
        } else {
            panic!("Problem opening the file: {error:?}");
        }
    });
}

fn func3() {
    // gives file if it returns OK(), throws default panic! otherwise.
    let greeting_file = File::open("hello.txt").unwrap();

    //similar to unwrap_or_else, this throws panic! and we only get to choose the message type.
    let greeting_file = File::open("hello.txt")
        .expect("hello.txt should be included in this project");
}

// Concise way of handling errors. 
// ? operator either returns Early Error on failure, otherwise it gives Ok(value)
// therefore, by chaining we can write more concise code, but we also leave error handling to the
// caller.
fn read_username_from_file() -> Result<String, io::Error> {
    let mut username = String::new();

    File::open("hello.txt")?.read_to_string(&mut username)?;

    Ok(username)
}

//in Rust nothing is stopping you from making main function return Result
//
// more generic version of this is :
// fn main() -> Result<(), Box<dyn Error>> {
fn main() -> Result<(),io::Error> {
    let mut username = String::new();


    File::open("hello.txt")?.read_to_string(&mut username)?;

    println!(username);

    Ok(()) // Returning an empty? Ok enum.
}


