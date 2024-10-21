from .cli import main as cli_main
from .tui import BeepyNetworkManagerApp


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        cli_main()
    else:
        BeepyNetworkManagerApp().run()


if __name__ == "__main__":
    main()
