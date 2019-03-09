import hashlib
import io

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class InvalidKey(RuntimeError):
    def __init__(self) -> None:
        super().__init__("the supplied key appears to be invalid")


class AESCipher:
    def __init__(self, key: str) -> None:
        self.key = hashlib.sha256(key.encode()).digest()
        self.chk = bytes(range(AES.block_size))

    def encrypt(self, data: bytes) -> bytes:
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(self.chk + pad(data, AES.block_size))
        with io.BytesIO() as handle:
            handle.write(iv)
            handle.write(ciphertext)
            handle.seek(0)
            return bytes(handle.read())

    def decrypt(self, enc: bytes) -> bytes:
        with io.BytesIO(enc) as handle:
            iv = handle.read(AES.block_size)
            assert len(iv) == AES.block_size
            ciphertext = handle.read()

        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        with io.BytesIO(cipher.decrypt(ciphertext)) as handle:
            chk = handle.read(AES.block_size)
            if chk != self.chk:
                raise InvalidKey
            data = unpad(handle.read(), AES.block_size)

        return data
