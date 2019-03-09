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


def read_database(key: str) -> T.Dict[str, T.Dict[str, str]]:
    aes = AESCipher(key)
    if not DB_FILE.exists():
        return {}
    return json.loads(
        zlib.decompress(aes.decrypt(DB_FILE.read_bytes())).decode()
    )


def write_database(key: str, db: T.Dict[str, T.Dict[str, str]]) -> None:
    aes = AESCipher(key)
    DB_FILE.write_bytes(
        aes.encrypt(
            zlib.compress(
                json.dumps(db).encode(), level=zlib.Z_BEST_COMPRESSION
            )
        )
    )


@contextlib.contextmanager
def database() -> T.Iterator[T.Dict[str, T.Dict[str, str]]]:
    key = getpass("Master password: ")
    db = read_database(key)
    old_db = copy.deepcopy(db)
    yield db
    if old_db != db:
        write_database(key, db)
