import contextlib
import copy
import json
import typing as T
import zlib
from getpass import getpass
from pathlib import Path

from .aes import AESCipher

DB_FILE = Path("~/.config/pw.dat").expanduser()


class PasswordAlreadyExists(RuntimeError):
    def __init__(self) -> None:
        super().__init__("password already exists")


class PasswordDoesNotExist(RuntimeError):
    def __init__(self) -> None:
        super().__init__("password does not exist")


@contextlib.contextmanager
def database() -> T.Iterator[T.Dict[str, T.Dict[str, str]]]:
    key = getpass("Master password: ")
    aes = AESCipher(key)

    db: T.Dict[str, T.Dict[str, str]]
    if DB_FILE.exists():
        db = json.loads(
            zlib.decompress(aes.decrypt(DB_FILE.read_bytes())).decode()
        )
    else:
        db = {}

    old_db = copy.deepcopy(db)

    yield db
    if old_db != db:
        DB_FILE.write_bytes(
            aes.encrypt(
                zlib.compress(
                    json.dumps(db).encode(), level=zlib.Z_BEST_COMPRESSION
                )
            )
        )
