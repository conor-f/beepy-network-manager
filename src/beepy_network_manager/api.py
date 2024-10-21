import logging
from typing import Dict, List, Optional
from .config import run_nmcli, WIFI_INTERFACE, get_wifi_networks, connect_to_wifi, disconnect_wifi, get_current_connection

logger = logging.getLogger(__name__)

def get_current_network() -> Optional[str]:
    current_connection = get_current_connection()
    return current_connection.get('name') if current_connection else None

def get_networks() -> List[Dict]:
    return get_wifi_networks()

def connect_to_network(ssid: str, password: Optional[str] = None):
    logger.info(f"Attempting to connect to: {ssid}")
    if connect_to_wifi(ssid, password):
        logger.info(f"Connected to {ssid}")
    else:
        logger.error(f"Failed to connect to {ssid}")

def disconnect_network():
    logger.info("Disconnecting from current network")
    if disconnect_wifi():
        logger.info("Disconnected from network")
    else:
        logger.info("No active connection to disconnect")
