from .lorenz import LorenzCipher

CIPHERS = {
    "lorenz": LorenzCipher,
    # z.B. später: "aes": AESCipher, "otp": OneTimePadCipher
}

def get_cipher(name: str):
    CipherClass = CIPHERS.get(name.lower())
    if CipherClass:
        return CipherClass()
    raise ValueError(f"Unsupported cipher: {name}")