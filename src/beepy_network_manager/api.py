import logging
import subprocess
from typing import Dict, List, Optional

WIFI_INTERFACE = None

logger = logging.getLogger(__name__)


async def get_wifi_interface():
    global WIFI_INTERFACE

    if WIFI_INTERFACE is not None:
        return WIFI_INTERFACE

    try:
        result = await run_nmcli(["device", "status"])
        for line in result.split("\n"):
            if "wifi" in line.lower():
                WIFI_INTERFACE = line.split()[0]
    except Exception:
        pass

    # Default to wlan0 if nmcli fails or no wifi interface is found
    WIFI_INTERFACE = "wlan0"

    return WIFI_INTERFACE


async def run_nmcli(args: List[str]) -> str:
    try:
        result = subprocess.run(
            ["nmcli"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error running nmcli: {e}")
        return ""


async def get_current_network() -> Optional[str]:
    output = await run_nmcli(["connection", "show", "--active"])
    for line in output.split("\n"):
        if await get_wifi_interface() in line:
            fields = line.split()
            return fields[0]

    return None


async def get_networks() -> List[Dict]:
    output = await run_nmcli(
        [
            "--fields",
            "SSID,SIGNAL,SECURITY",
            "--terse",
            "device",
            "wifi",
            "list",
        ]
    )
    networks = []
    for line in output.split("\n"):
        if line:
            ssid, signal, security = line.split(":")
            networks.append(
                {
                    "ssid": ssid,
                    "signal": signal,
                    "security": security if security else "Open",
                    "quality": str(
                        int(signal) * 2
                    ),  # Approximating quality as twice the signal strength
                    "encrypted": security != "Open",
                }
            )
    return networks


async def connect_to_network(
    ssid: str,
    password: Optional[str] = None,
) -> bool:
    logger.info(f"Attempting to connect to: {ssid}")

    params = ["device", "wifi", "connect", ssid]

    if password:
        params.extend(["password", password])

    params.extend(["ifname", await get_wifi_interface()])

    result = await run_nmcli(params)

    if "successfully activated" in result.lower():
        logger.info(f"Connected to {ssid}")
        return True
    else:
        logger.error(f"Failed to connect to {ssid}")
        return False


async def disconnect_network() -> bool:
    logger.info("Disconnecting from current network")
    result = await run_nmcli(
        ["device", "disconnect", await get_wifi_interface()]
    )
    if "successfully disconnected" in result.lower():
        logger.info("Disconnected from network")
        return True
    else:
        logger.info("No active connection to disconnect")
        return False
