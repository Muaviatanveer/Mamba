use std::io::{Read, Write};
use std::net::TcpListener;

fn main() {
    let listener = TcpListener::bind("0.0.0.0:3003").unwrap();
    println!("🦀 Rust Server running on http://localhost:3003");

    let response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 73\r\n\r\n{\"name\": \"Muavia\", \"project\": \"Mamba\", \"role\": \"AI Engineer\", \"version\": \"0.1.0\"}";

    for stream in listener.incoming() {
        if let Ok(mut stream) = stream {
            let mut buffer = [0; 1024];
            let _ = stream.read(&mut buffer);
            let _ = stream.write_all(response.as_bytes());
        }
    }
}