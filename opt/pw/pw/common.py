import random
import subprocess
import time

DEFAULT_WAIT = 5


def set_clipboard(text: str) -> None:
    subprocess.run(["xclip"], input=text, encoding="ascii")


def clear_clipboard() -> None:
    subprocess.run(["xclip"], input=b"\x00")


def set_clipboard_for(text: str, wait: int) -> None:
    set_clipboard(text)
    print(f"Clipboard updated, waiting {wait} second to clear")
    time.sleep(wait)
    clear_clipboard()


def get_random_pass(length: int = 25) -> str:
    alpha = "abcdefghijklmnopqrstuvwxyz"
    alpha += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alpha += "0123456789"
    alpha += "_-"
    while True:
        password = "".join(random.choice(alpha) for _ in range(length))
        if not password.startswith(" ") and not password.endswith(" "):
            return password
