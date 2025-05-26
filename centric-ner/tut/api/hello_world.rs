// Best way to learn the basics of rust is using following these resources:
// Rustlings (interactive exercises with quizzes) https://github.com/rust-lang/rustlings
// Official Rust documentation : https://doc.rust-lang.org/book/
// Rust official rust docs with quizzes : https://doc.rust-lang.org/book/
// Most of the examples below are from rustlings tutorial.

fn main() {
    println!("Hello World"); // println is special, and normal functions do not use '!', ! is used to denote that it is a macro.
}

fn language_quirk_1(){
    let x = 5; // all variables are immutable by default.
    // x = 10 will fail

    let mut y = 5; // mut for mutability.

    y = 10; //works
}

// squares input values
fn language_quirk_2(num:i32) -> i32 {
    num*2 //equals to return num*2; <-- In rust if last statement of a function does not have semicolon, it will be used as return value.
}

// When assigning variables, you can assign them conditionally, here we are combining implicit return and conditional assignment of a variable.
fn language_quirk_3(input: i32) -> bool {
    let variable :bool = if input == 0 {
        true
    } else if input < 100 {
        false
    } else {
        true
    }
}

fn language_quirk_4(){
    let char = 'C'; // Chars use single quote
    let string = "Word" // strings use double quote.
}

fn language_quirk_5(){
    let a = [0;100]; // Creates an array of 100 zeros.
}

fn language_quirk_6(){
    //slices of an array by reference & is symbol for reference.
    let a = [1,2,3,4,5];

    let slice = &a[1..4];

    println!(slice); // outputs [2,3,4]
}

fn language_quirk_7(){
    let info = ("Slim Shady", 50); // Tuple

    let (name, age) = info; // You can destructure a tuple

    let name2 = info.0; // you can also access tuples by using indexes directly.
}

fn language_quirk_8(){
    let first = vec![1,2,3,4];

    let mut second : Vec<i64>= Vec::new(); // need to make vector mutable for dynamic vectors.
    second.push(10);
    second.pop();
}