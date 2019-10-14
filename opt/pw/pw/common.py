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
