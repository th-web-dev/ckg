use pyo3::prelude::*;
use sha2::{Sha256, Digest};
use crate::shared::*;

#[pyfunction]
fn generate_noise_field_py(token: &str, size: usize, scale: f64) -> PyResult<Vec<Vec<f64>>> {
    Ok(generate_noise_matrix(token, size, scale))
}

#[pyfunction]
fn rotate_token_py(current_token: &str, message_hash: &str) -> PyResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(current_token.as_bytes());
    hasher.update(message_hash.as_bytes());
    let result = hasher.finalize();
    Ok(hex::encode(result))
}

#[pymodule]
fn chaoscrypto_noise(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_noise_field_py, m)?)?;
    m.add_function(wrap_pyfunction!(rotate_token_py, m)?)?;
    Ok(())
}
