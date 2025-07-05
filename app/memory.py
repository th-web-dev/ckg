import hashlib
import numpy as np
import chaoscrypto_noise

memory_fields = {}

def generate_seed(token: str) -> int:
    return int(hashlib.sha256(token.encode()).hexdigest(), 16) % (2**31)


def generate_noise_field_opensimplex(token: str, size=100, scale=0.1) -> np.ndarray:
    field = chaoscrypto_noise.generate_noise_field_py(token, size, scale)

    return np.array(field)


def extract_lorenz_params(field: np.ndarray, coord: tuple[int, int]) -> tuple[float, float, float]:
    """Liest 3 Werte aus dem Noise-Field und wandelt sie in Lorenz-Startwerte um"""
    x, y = coord

    # hole 3 benachbarte Werte für x0, y0, z0
    val1 = field[x % field.shape[0], y % field.shape[1]]
    val2 = field[(x+1) % field.shape[0], y % field.shape[1]]
    val3 = field[x % field.shape[0], (y+1) % field.shape[1]]

    # skalieren, damit Werte im Lorenz-tauglichen Bereich liegen
    x0 = val1 * 20 + 10    # z.B. zwischen -10 und +30
    y0 = val2 * 20 + 10
    z0 = val3 * 20 + 10

    return x0, y0, z0


def get_lorenz_seed_from_token(token: str, coord: tuple[int, int]) -> tuple[float, float, float]:
    field = generate_noise_field_opensimplex(token, size=100, scale=0.1)
    x = field[coord[0]][coord[1]]
    y = field[(coord[0] + 5) % 100][(coord[1] + 5) % 100]
    z = field[(coord[0] + 10) % 100][(coord[1] + 10) % 100]
    return x, y, z

def store_noise_field(user_id: str, field):
    memory_fields[user_id] = field

def get_noise_field(user_id: str):
    return memory_fields.get(user_id)