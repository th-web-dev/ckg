class LorenzCipher:
    def __init__(self, sigma=10, rho=28, beta=8 / 3, dt=0.01, noise=None, steps_per_char=100):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.dt = dt
        self.noise = noise
        self.steps_per_char = steps_per_char

    def _get_seed_from_coord(self, coord):
        x, y = coord
        n = self.noise
        return (
            n[x][y],
            n[(x + 1) % len(n)][y],
            n[x][(y + 1) % len(n[0])]
        )

    def _generate_keystream(self, text_len, seed):
        x, y, z = seed
        keystream = []

        for i in range(text_len):
            for _ in range(self.steps_per_char):
                dx = self.sigma * (y - x)
                dy = x * (self.rho - z) - y
                dz = x * y - self.beta * z

                x += dx * self.dt
                y += dy * self.dt
                z += dz * self.dt

            byte = int(abs(z * 1e6)) % 256
            keystream.append(byte)

        return keystream

    def encrypt(self, plaintext: str, coord: tuple[int, int]) -> dict:
        seed = self._get_seed_from_coord(coord)
        keystream = self._generate_keystream(len(plaintext), seed)

        encrypted = ''.join(chr(ord(c) ^ k) for c, k in zip(plaintext, keystream))

        formatted_log = [
            {"type": "line", "text": f"> Starting encryption at coord {coord}"},
            {"type": "line", "text": f"> Lorenz seed: [{seed[0]:.6f}, {seed[1]:.6f}, {seed[2]:.6f}]"},
            {"type": "log",  "text": f"> Server keystream bytes: {keystream}"},
            {"type": "line", "text": f"> Encrypted result: '{encrypted}'"}
        ]

        return {
            "encrypted": encrypted,
            "formatted": formatted_log
        }

    def decrypt(self, ciphertext: str, coord: tuple[int, int]) -> dict:
        seed = self._get_seed_from_coord(coord)
        keystream = self._generate_keystream(len(ciphertext), seed)

        decrypted = ''.join(chr(ord(c) ^ k) for c, k in zip(ciphertext, keystream))

        formatted_log = [
            {"type": "line", "text": f"> Starting decryption at coord {coord}"},
            {"type": "line", "text": f"> Lorenz seed: [{seed[0]:.6f}, {seed[1]:.6f}, {seed[2]:.6f}]"},
            {"type": "log",  "text": f"> Server keystream bytes: {keystream}"},
            {"type": "line", "text": f"> Decrypted result: '{decrypted}'"}
        ]

        return {
            "decrypted": decrypted,
            "formatted": formatted_log
        }
