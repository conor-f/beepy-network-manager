import logging
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Static,
)

from beepy_network_manager.api import (
    ConnectionState,
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


class IncorrectPasswordModal(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Center(
            Static("Incorrect Password", id="incorrect-password-title"),
            Button("OK", variant="primary", id="ok-button"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


class PasswordInput(ModalScreen[Optional[str]]):
    BINDINGS = [("enter", "connect", "Connect")]

    def compose(self) -> ComposeResult:
        yield Static("Enter Password", id="password-title")
        yield Input(placeholder="Password", password=True, id="password-input")
        yield Horizontal(
            Button("Connect", variant="primary", id="connect-button"),
            Button("Cancel", variant="default", id="cancel-button"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "connect-button":
            self.action_connect()
        else:
            self.dismiss(None)

    def action_connect(self) -> None:
        password = self.query_one("#password-input").value
        self.dismiss(password)

    def on_input_submitted(self) -> None:
        self.action_connect()


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

        await self.refresh_networks()
        await self.update_current_network()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        network = str(event.item.get_child_by_type(Label).renderable)
        self.logger.info(f"Network selected: {network}")
        await self.connect_to_network(network)

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

    async def input_password_callback(
        self, network: str, password: Optional[str]
    ):
        connection_result = await connect_to_network(network, password)

        self.logger.info("B")
        self.logger.info(connection_result)
        if connection_result == ConnectionState.FAILED:
            self.logger.info("C")
            await self.push_screen(IncorrectPasswordModal())
        self.logger.info("D")
        await self.update_current_network()

    async def connect_to_network(self, network: str) -> None:
        self.logger.info(f"Connecting to network: {network}")

        loading = self.query_one("#loading")
        networks_view = self.query_one("#networks")

        loading.styles.display = "block"
        networks_view.styles.display = "none"

        # First, try to connect without a password
        connection_result = await connect_to_network(network)

        if connection_result == ConnectionState.PASSWORD_REQUIRED:
            # If encryption is required, show the password input modal
            await self.push_screen(
                PasswordInput(),
                lambda password: self.input_password_callback(
                    network, password
                ),
            )

        if connection_result == ConnectionState.SUCCESS:
            self.logger.info(f"Successfully connected to {network}")
        elif connection_result == ConnectionState.FAILED:
            self.logger.info(f"Failed to connect to {network}")

        await self.update_current_network()

        loading.styles.display = "none"
        networks_view.styles.display = "block"

    async def action_disconnect(self) -> None:
        self.logger.info("Disconnecting from network")

        loading = self.query_one("#loading")
        networks_view = self.query_one("#networks")

        loading.styles.display = "block"
        networks_view.styles.display = "none"

        await disconnect_network()
        await self.update_current_network()

        loading.styles.display = "none"
        networks_view.styles.display = "block"

    async def update_current_network(self) -> None:
        self.logger.info("Getting current network...")
        current_network = await get_current_network()

        try:
            if current_network:
                self.query_one("#current_network").update(
                    f"Connected to: {current_network}"
                )
            else:
                self.query_one("#current_network").update(
                    "Not connected to any network"
                )
        except Exception as e:
            self.logger.error(f"Error updating current network: {str(e)}")
            # Happens when the network is looking for a password or other
            # expected situations.
            pass

    def action_quit(self) -> None:
        self.logger.info("Quitting application")
        self.exit()

    async def action_refresh(self) -> None:
        self.logger.info("Refreshing networks")
        await self.refresh_networks()

    def action_move_down(self) -> None:
        list_view = self.query_one("#networks")
        list_view.action_cursor_down()

    def action_move_up(self) -> None:
        list_view = self.query_one("#networks")
        list_view.action_cursor_up()
