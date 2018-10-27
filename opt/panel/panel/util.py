import subprocess


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True)
