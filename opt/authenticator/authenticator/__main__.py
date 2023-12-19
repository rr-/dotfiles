from authenticator.cli import run


def main() -> None:
    try:
        run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
