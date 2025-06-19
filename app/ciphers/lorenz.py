from .base import BaseCipher
from app.utils import format_log
from app.memory import get_lorenz_seed_from_token

class LorenzCipher(BaseCipher):
    def __init__(self, sigma=10, rho=28, beta=8/3, dt=0.01):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.dt = dt

    def encrypt(self, plaintext: str, token: str = None, coord: tuple[int, int] = (0, 0)) -> dict:
        if token:
            x, y, z = get_lorenz_seed_from_token(token, coord)
        else:
            x, y, z = 1.0, 1.0, 1.0

        log = [f"Starte Lorenz-Verschlüsselung (Seed aus Token '{token}', Coord={coord})"]
        key_bits = []

        for i, char in enumerate(plaintext):
            dx = self.sigma * (y - x)
            dy = x * (self.rho - z) - y
            dz = x * y - self.beta * z
            x += dx * self.dt
            y += dy * self.dt
            z += dz * self.dt

            log.append(f"Step {i}: x={x:.4f}, y={y:.4f}, z={z:.4f}")
            key_bits.append(1 if x > 0 else 0)

        encrypted = ''.join(chr(ord(c) ^ k) for c, k in zip(plaintext, key_bits))
        log.append(f"Verschlüsselt: {encrypted}")

        return {
            "encrypted": encrypted,
            "log": log,
            "formatted": format_log(log, "Encrypted Result", encrypted)
        }

    def decrypt(self, ciphertext: str, token: str = None, coord: tuple[int, int] = (0, 0)) -> dict:
        return self.encrypt(ciphertext, token=token, coord=coord)
