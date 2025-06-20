use noise::{NoiseFn, OpenSimplex, Seedable};
use sha2::{Digest, Sha256};
use wasm_bindgen::prelude::*;
use js_sys::{Array, JsString};

#[wasm_bindgen]
pub fn generate_noise_field(token: &str, size: usize, scale: f32) -> Array {
    let seed = hash_token(token);
    let mut noise = OpenSimplex::default();
    noise = noise.set_seed(seed);

    let result = Array::new();

    for i in 0..size {
        for j in 0..size {
            let value = noise.get([i as f64 * scale as f64, j as f64 * scale as f64]);
            result.push(&JsValue::from_f64(value));
        }
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
pub fn rotate_token(current_token: &str, message_hash: &str) -> JsString {
    let mut hasher = Sha256::new();
    hasher.update(current_token.as_bytes());
    hasher.update(message_hash.as_bytes());
    let result = hasher.finalize();
    JsString::from(hex::encode(&result))
}
