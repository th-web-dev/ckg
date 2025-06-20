use noise::{NoiseFn, OpenSimplex};
use sha2::{Digest, Sha256};

pub fn hash_token(token: &str) -> u32 {
    let mut hasher = Sha256::new();
    hasher.update(token.as_bytes());
    let result = hasher.finalize();
    u32::from_le_bytes([result[0], result[1], result[2], result[3]])
}

pub fn generate_noise_matrix(token: &str, size: usize, scale: f64) -> Vec<Vec<f64>> {
    let seed = hash_token(token);
    let noise = OpenSimplex::new(seed);

    let mut field = vec![vec![0.0; size]; size];

    for i in 0..size {
        for j in 0..size {
            field[i][j] = noise.get([i as f64 * scale, j as f64 * scale]);
        }
    }

    field
}
