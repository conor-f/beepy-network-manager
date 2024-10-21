import subprocess
from pathlib import Path
from typing import List, Dict
import tomli


def load_config():
    pyproject_path = Path(__file__).parents[3] / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomli.load(f)

    return pyproject_data.get("tool", {}).get("beepy_network_manager", {})


CONFIG = {}  # load_config()


def get_wifi_interface():
    try:
        result = run_nmcli(["device", "status"])
        for line in result.split("\n"):
            if "wifi" in line.lower():
                return line.split()[0]
    except Exception:
        pass
    return "wlp53s0"  # Default to wlan0 if nmcli fails or no wifi interface is found


WIFI_INTERFACE = CONFIG.get("wifi_interface", get_wifi_interface())


def run_nmcli(args: List[str]) -> str:
    try:
        result = subprocess.run(
            ["nmcli"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running nmcli: {e}")
        return ""


def get_wifi_networks() -> List[Dict[str, str]]:
    output = run_nmcli(
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


def connect_to_wifi(ssid: str, password: str = "") -> bool:
    if password:
        result = run_nmcli(
            [
                "device",
                "wifi",
                "connect",
                ssid,
                "password",
                password,
                "ifname",
                WIFI_INTERFACE,
            ]
        )
    else:
        result = run_nmcli(
            ["device", "wifi", "connect", ssid, "ifname", WIFI_INTERFACE]
        )
    return "successfully activated" in result.lower()


def disconnect_wifi() -> bool:
    result = run_nmcli(["device", "disconnect", WIFI_INTERFACE])
    return "successfully disconnected" in result.lower()


def get_current_connection() -> Dict[str, str]:
    output = run_nmcli(["connection", "show", "--active"])
    for line in output.split("\n"):
        if WIFI_INTERFACE in line:
            fields = line.split()
            return {
                "name": fields[0],
                "uuid": fields[1],
                "type": fields[2],
                "device": fields[3],
            }
    return {}
