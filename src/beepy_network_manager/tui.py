import logging
from asyncio import create_task, sleep

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import (
    Footer,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Static,
)

from beepy_network_manager.api import (
    connect_to_network,
    disconnect_network,
    get_current_network,
    get_networks,
)

# Set up logging
logging.basicConfig(
    filename="/tmp/beepy_network_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BeepyNetworkManagerApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh Networks", show=True),
        Binding("d", "disconnect", "Disconnect", show=True),
        Binding("j", "move_down", "Down", show=True),
        Binding("k", "move_up", "Up", show=True),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    def compose(self) -> ComposeResult:
        self.logger.info("Composing BeepyNetworkManagerApp")
        yield Static("Beepy Network Manager", id="title")
        yield LoadingIndicator(id="loading")
        yield ListView(id="networks")
        yield Static(id="current_network")
        yield Footer()

    async def on_mount(self) -> None:
        self.logger.info("BeepyNetworkManagerApp mounted")
        create_task(self.refresh_networks())
        create_task(self.update_current_network())

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        network = str(event.item.get_child_by_type(Label).renderable)
        self.logger.info(f"Network selected: {network}")
        create_task(self.connect_to_network(network))

    async def refresh_networks(self) -> None:
        self.logger.info("Refreshing networks")

        loading = self.query_one("#loading")
        networks_view = self.query_one("#networks")

        loading.styles.display = "block"
        networks_view.styles.display = "none"

        networks = await get_networks()

        self.logger.info(f"Found {len(networks)} networks")

        networks_view.clear()
        unique_ssids = set()

        for network in networks:
            ssid = network["ssid"]
            if ssid not in unique_ssids:
                unique_ssids.add(ssid)
                networks_view.append(ListItem(Label(ssid)))

        self.logger.info(f"Displaying {len(unique_ssids)} unique networks")

        loading.styles.display = "none"
        networks_view.styles.display = "block"

    async def connect_to_network(self, network: str) -> None:
        self.logger.info(f"Connecting to network: {network}")
        await connect_to_network(network)
        await self.update_current_network()

    async def action_disconnect(self) -> None:
        self.logger.info("Disconnecting from network")
        await disconnect_network()
        await self.update_current_network()

    async def update_current_network(self) -> None:
        while True:
            await sleep(5)
            self.logger.info("Getting current network...")
            current_network = await get_current_network()

            if current_network:
                self.query_one("#current_network").update(
                    f"Connected to: {current_network}"
                )
            else:
                self.query_one("#current_network").update(
                    "Not connected to any network"
                )

    def action_quit(self) -> None:
        self.logger.info("Quitting application")
        self.exit()

    def action_refresh(self) -> None:
        self.logger.info("Refreshing networks")
        create_task(self.refresh_networks())

    def action_move_down(self) -> None:
        list_view = self.query_one("#networks")
        list_view.action_cursor_down()

    def action_move_up(self) -> None:
        list_view = self.query_one("#networks")
        list_view.action_cursor_up()
