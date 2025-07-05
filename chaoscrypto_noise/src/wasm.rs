use wasm_bindgen::prelude::*;
use js_sys::Array;
use sha2::{Sha256, Digest}; 
use crate::shared::*;
#[wasm_bindgen]
pub fn generate_noise_field(token: &str, size: usize, scale: f64) -> js_sys::Array {
    let matrix = generate_noise_matrix(token, size, scale);
    let result = js_sys::Array::new();

    for row in matrix {
        let js_row = js_sys::Array::new();
        for val in row {
            js_row.push(&JsValue::from_f64(val));
        }
        result.push(&js_row);
    }

    result
}

#[wasm_bindgen]
pub fn rotate_token(current_token: &str, message_hash: &str) -> String {
    let mut hasher = sha2::Sha256::new();
    hasher.update(current_token.as_bytes());
    hasher.update(message_hash.as_bytes());
    let result = hasher.finalize();
    hex::encode(result)
}
