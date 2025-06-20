use noise::{NoiseFn, OpenSimplex};
use sha2::{Digest, Sha256};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn generate_noise_field(token: &str, size: usize, scale: f32) -> js_sys::Array {
    let seed = hash_token(token);
    let noise = OpenSimplex::new(seed);

    let result = js_sys::Array::new();

    for i in 0..size {
        let row = js_sys::Array::new();
        for j in 0..size {
            let value = noise.get([i as f64 * scale as f64, j as f64 * scale as f64]);
            row.push(&JsValue::from_f64(value));
        }
        result.push(&row);
    }

    result
}

fn hash_token(token: &str) -> u32 {
    let mut hasher = Sha256::new();
    hasher.update(token.as_bytes());
    let result = hasher.finalize();
    u32::from_le_bytes([result[0], result[1], result[2], result[3]])
}

#[wasm_bindgen]
pub fn rotate_token(current_token: &str, message_hash: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(current_token.as_bytes());
    hasher.update(message_hash.as_bytes());
    let result = hasher.finalize();
    hex::encode(&result)
}
