import argparse
import asyncio
import logging
import sys
import traceback

from beepy_network_manager.api import (
    connect_to_network,
    disconnect_network,
    get_current_network,
    get_networks,
)

logger = logging.getLogger(__name__)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler("/tmp/beepy_network_manager.log")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Stream handler (for stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter("%(message)s")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)


async def list_networks():
    try:
        networks = await get_networks()
        if networks:
            logger.info(f"Found {len(networks)} networks:")
            for network in networks:
                ssid = network["ssid"].replace(
                    "!", "\\!"
                )  # Escape exclamation marks for display
                logger.info(
                    f"- \"{ssid}\" - Signal: {network['signal']} - "
                    f"Quality: {network['quality']} - "
                    f"Encrypted: {'Yes' if network['encrypted'] else 'No'}"
                )
        else:
            logger.info("No networks found.")
    except Exception as e:
        logger.error(f"Error listing networks: {e}")


async def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Beepy Network Manager CLI")
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
    )

    subparsers.add_parser("list", help="List available networks")

    connect_parser = subparsers.add_parser(
        "connect", help="Connect to a network"
    )
    connect_parser.add_argument(
        "ssid", help="SSID of the network to connect", type=str, nargs="+"
    )
    connect_parser.add_argument("--password", help="Password for the network")

    subparsers.add_parser("disconnect", help="Disconnect from current network")

    subparsers.add_parser("status", help="Show current network status")

    args = parser.parse_args()

    try:
        if args.command == "list":
            await list_networks()
        elif args.command == "connect":
            try:
                ssid = " ".join(args.ssid)
                await connect_to_network(ssid, args.password)
                logger.info(f'Successfully connected to "{ssid}"')
            except Exception as e:
                logger.error(f'Failed to connect to "{args.ssid}": {e}')
        elif args.command == "disconnect":
            await disconnect_network()
        elif args.command == "status":
            current_network = await get_current_network()
            if current_network:
                logger.info(f"Currently connected to: {current_network}")
            else:
                logger.info("Not connected to any network")
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error("Detailed exception information:")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
