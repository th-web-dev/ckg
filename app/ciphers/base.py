class BaseCipher:
    def encrypt(self, plaintext: str) -> dict:
        raise NotImplementedError("encrypt() must be implemented")

    def decrypt(self, ciphertext: str) -> dict:
        raise NotImplementedError("decrypt() must be implemented")
