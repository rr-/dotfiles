import sys


def move_cursor_up(num: int) -> None:
    sys.stdout.write("\x1B[{}F".format(num))


def erase_whole_line() -> None:
    sys.stdout.write("\x1B[999D\x1B[K")
