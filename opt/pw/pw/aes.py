import hashlib

from Crypto import Random
from Crypto.Cipher import AES


class InvalidKey(RuntimeError):
    def __init__(self) -> None:
        super().__init__("the supplied key appears to be invalid")


class AESCipher:
    def __init__(self, key: str) -> None:
        self.key = hashlib.sha256(key.encode()).digest()
        self.check = bytes(range(AES.block_size))

    def encrypt(self, dec: bytes) -> bytes:
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(self._pad(dec) + self.check)

    def decrypt(self, enc: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, enc[: AES.block_size])
        tmp = cipher.decrypt(enc[AES.block_size :])
        if tmp[-AES.block_size :] != self.check:
            raise InvalidKey
        return self._unpad(tmp[: -AES.block_size])

    @staticmethod
    def _pad(source: bytes) -> bytes:
        bs = AES.block_size * 2
        return source + (bs - len(source) % bs) * bytes(
            [bs - len(source) % bs]
        )

    @staticmethod
    def _unpad(source: bytes) -> bytes:
        return source[: -ord(source[len(source) - 1 :])]
