import argparse
import sys
import time
from pathlib import Path

import xdg
from authenticator.data import ClientData, ClientFile, MissingKeyError
from authenticator.hotp import HOTP
from authenticator.util.cli import erase_whole_line, move_cursor_up

DATA_FILE = Path(xdg.XDG_CONFIG_HOME) / "authenticator/devices.json"
REFRESH_TIME = 5

THROBBER_CHARS = "  ▏▎▍▌▋▊▉█"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("client_id", nargs="?")
    return parser.parse_args()


def get_throbber(current_value: float | int, max_value: int) -> str:
    return THROBBER_CHARS[
        ((len(THROBBER_CHARS) - 1) * int(current_value)) // max_value
    ]


def generate(hotp: HOTP, cds_to_calc: list[ClientData]) -> int | float | None:
    expiration_guard = 10**6
    most_recent_expiration: int | float = expiration_guard

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

    move_cursor_up(len(cds_to_calc))

    if most_recent_expiration >= expiration_guard:
        return None

    return most_recent_expiration


def run_once(hotp: HOTP, cd: ClientData) -> None:
    code_string, remaining_seconds = hotp.generate_code_from_time(
        cd.shared_secret,
        code_length=cd.password_length,
        period=cd.period,
    )
    print(code_string)


def run_continuously(hotp: HOTP, cds: list[ClientData]) -> None:
    while True:
        soonest_expiration = generate(hotp, cds)
        if soonest_expiration is None:
            break
        time.sleep(1)


def run() -> None:
    args = parse_args()

    file = ClientFile(DATA_FILE)
    cds: list[ClientData] = []
    if file.exists():
        cds = file.load()

    if not cds:
        print("No HOTP/TOTP configurations found.", file=sys.stderr)
        return

    hotp = HOTP()
    if args.client_id:
        try:
            run_once(hotp, file.get_client_data(args.client_id))
        except MissingKeyError:
            print(
                "No matching HOTP/TOTP configuration found.", file=sys.stderr
            )
    else:
        run_continuously(hotp, cds)
