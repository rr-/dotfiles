import io
import shutil
import subprocess
import typing as T


def print_in_columns(items: T.Iterable[str], file: T.TextIO) -> None:
    items = [f"- {item} " for item in items]
    column_size = max((len(item) for item in items), default=5)
    term_size = shutil.get_terminal_size()
    columns = term_size.columns // column_size
    while items:
        row = ""
        for _ in range(columns):
            if not items:
                break
            item = items.pop(0)
            row += f"{item:<{column_size}s}"
        row = row.rstrip()
        print(row, end="\n" if len(row) < term_size.columns else "", file=file)
    print(file=file)


def pager(text: str) -> None:
    """Page through text by feeding it to another program."""
    proc = subprocess.Popen("less -r", shell=True, stdin=subprocess.PIPE)
    try:
        with io.TextIOWrapper(proc.stdin, errors="backslashreplace") as pipe:
            try:
                pipe.write(text)
            except KeyboardInterrupt:
                # We've hereby abandoned whatever text hasn't been written,
                # but the pager is still in control of the terminal.
                pass
    except OSError:
        pass  # Ignore broken pipes caused by quitting the pager program.
    while True:
        try:
            proc.wait()
            break
        except KeyboardInterrupt:
            # Ignore ctl-c like the pager itself does.  Otherwise the pager is
            # left running and the terminal is in raw mode and unusable.
            pass
