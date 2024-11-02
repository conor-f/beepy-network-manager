import asyncio
import sys

from .cli import main as cli_main
from .tui import BeepyNetworkManagerApp


async def main() -> None:
    if len(sys.argv) > 1:
        await cli_main()
    else:
        app = BeepyNetworkManagerApp()
        await app.run_async()


def run_main():
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
