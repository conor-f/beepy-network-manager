import asyncio
import logging
from enum import Enum
from typing import Dict, List, Optional

WIFI_INTERFACE = None


class ConnectionState(Enum):
    SUCCESS = "success"
    PASSWORD_REQUIRED = "password_required"
    FAILED = "failed"


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

                return WIFI_INTERFACE
    except Exception:
        pass

    # Default to wlan0 if nmcli fails or no wifi interface is found
    return "wlan0"


async def run_nmcli(args: List[str]) -> str:
    process = await asyncio.create_subprocess_exec(
        "nmcli",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return stdout.decode().strip()
    else:
        logger.error(f"Error running nmcli: {stderr.decode().strip()}")
        return stderr.decode().strip()


async def get_current_network() -> Optional[str]:
    output = await run_nmcli(["-t", "-f", "active,ssid", "dev", "wifi"])

    for line in output.split("\n"):
        if "yes" in line:
            fields = line.split(":")
            return fields[1]

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
            "--rescan",
            "yes",
        ]
    )
    networks = []
    for line in output.split("\n"):
        if line:
            ssid, signal, security = line.split(":")
            if ssid:
                networks.append(
                    {
                        "ssid": ssid,
                        "signal": signal,
                        "security": security if security else "Open",
                        "quality": str(int(signal) * 2),
                        "encrypted": security != "Open",
                    }
                )
    return networks


async def connect_to_network(
    ssid: str,
    password: Optional[str] = None,
) -> ConnectionState:
    logger.info(f"Attempting to connect to: {ssid}")

    params = ["device", "wifi", "connect", ssid]

    if password:
        params.extend(["password", password])

    params.extend(["ifname", await get_wifi_interface()])

    result = await run_nmcli(params)

    if "successfully activated" in result.lower():
        logger.info(f"Connected to {ssid}")
        return ConnectionState.SUCCESS
    elif "secrets were required, but not provided" in result.lower():
        return ConnectionState.PASSWORD_REQUIRED
    else:
        logger.error(f"Failed to connect to {ssid}")
        return ConnectionState.FAILED


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
