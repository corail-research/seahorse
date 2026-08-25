import builtins
import os
import platform
import subprocess

from loguru import logger

from seahorse.game.io_stream import EventMaster, EventSlave


class GUIClient(EventSlave):
    """
    Client for connecting to and launching a graphical user interface.

    This class handle GUI-specific events and can launch external
    applications or web interfaces.

    Attributes:
        id (int): Unique identifier for this GUI client instance.
        wrapped_id (int): Alias for the ID for consistency with parent class.
        path (str | None): Path or URL to open when the GUI client starts.
        sid (str | None): Socket.IO session ID (None until connected).
    """

    def __init__(self, path: str | None = None) -> None:
        """
        Initializes the GUIClient with optional path for external launch.

        Args:
            path:
                Optional file path or URL to open
                when the GUI client activates.
                If provided, this will be opened
                in the system's default application.
        """
        super().__init__()
        self.id = builtins.id(self)
        self.wrapped_id = self.id
        self.path = path
        self.sid = None
        self.activate("__GUI__" + str(self.id))

    @staticmethod
    def open_file(url: str):
        """
        Opens a file or URL using the system's default application.

        Cross-platform method that handles different operating systems:
        - Windows: Uses os.startfile()
        - Linux: Uses xdg-open or wslview for WSL
        - macOS: Uses the 'open' command

        Args:
            url (str): File path or URL to open.

        Raises:
            Exception:
                If the platform is not recognized and cannot open the URL.
        """
        try:
            os.startfile(url)
        except AttributeError:
            try:
                system = platform.system()
                if system == "Linux":
                    # Handle WSL specifically
                    if "microsoft" in platform.uname().release.lower():
                        subprocess.check_call(["wslview", url])
                    else:
                        subprocess.check_call(["xdg-open", url])
                elif system == "Darwin":
                    subprocess.check_call(["open", url])
                else:
                    msg = "Unexpected platform"
                    raise Exception(msg)
            except Exception as e:
                logger.debug(f"Could not open URL: {e}")

    async def listen(self, **_) -> None:
        """
        Listens for GUI connections and optionally opens external applications.

        If a path was provided during initialization,
        opens that path using the system's default application.
        Then waits for the GUI client to be identified
        by the EventMaster and stores the session ID.

        Args:
            **_ (dict[str, _]):
                Accepts any additional keyword arguments (ignored).
        """
        if self.path:
            GUIClient.open_file(self.path)
        idmap = await EventMaster.get_instance()\
            .wait_for_identified_client("__GUI__", self.id)
        self.sid = idmap["sid"]
