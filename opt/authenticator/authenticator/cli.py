import time
from pathlib import Path

import xdg
from authenticator.data import ClientData, ClientFile
from authenticator.hotp import HOTP
from authenticator.util.cli import erase_whole_line, move_cursor_up

DATA_FILE = Path(xdg.XDG_CONFIG_HOME) / "authenticator/devices.json"
REFRESH_TIME = 5

THROBBER_CHARS = "  ▏▎▍▌▋▊▉█"


def get_throbber(current_value: float | int, max_value: int) -> str:
    return THROBBER_CHARS[
        ((len(THROBBER_CHARS) - 1) * int(current_value)) // max_value
    ]


def generate(cds_to_calc: list[ClientData]) -> int | float | None:
    expiration_guard = 10**6
    most_recent_expiration: int | float = expiration_guard

    hotp = HOTP()
    for cd in cds_to_calc:
        code_string, remaining_seconds = hotp.generate_code_from_time(
            cd.shared_secret,
            code_length=cd.password_length,
            period=cd.period,
        )
        most_recent_expiration = min(most_recent_expiration, remaining_seconds)
        erase_whole_line()
        print(
            get_throbber(remaining_seconds, cd.period),
            f"{cd.client_id}: {code_string} "
            f"(expires in {remaining_seconds} seconds)",
        )

    move_cursor_up(len(cds_to_calc) + 1)

    if most_recent_expiration >= expiration_guard:
        return None

    return most_recent_expiration


def run() -> None:
    file = ClientFile(DATA_FILE)
    if not file.exists():
        file.save([])

    cds = file.load()
    if not cds:
        print("No HOTP/TOTP configurations found.")
        return

    first_time = True
    while True:
        if not first_time:
            print("")
        first_time = False
        soonest_expiration = generate(cds)
        if soonest_expiration is None:
            break
        time.sleep(1)
