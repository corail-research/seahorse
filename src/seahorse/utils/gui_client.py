import builtins
import os
import platform
import subprocess
from collections.abc import Coroutine
from typing import Any, Optional

from loguru import logger

from seahorse.game.io_stream import EventMaster, EventSlave


class GUIClient(EventSlave):
    def __init__(self, path:Optional[str]=None) -> None:
        self.id = builtins.id(self)
        self.wrapped_id = self.id
        self.path = path
        self.sid = None

    @staticmethod
    def open_file(url):
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

    async def listen(self,**_) -> Coroutine[Any, Any, None]:
        if self.path:
            GUIClient.open_file(self.path)
        idmap = await EventMaster.get_instance().wait_for_identified_client("__GUI__",self.id)
        self.sid = idmap["sid"]
