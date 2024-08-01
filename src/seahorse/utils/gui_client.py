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
                if platform.system() == "Linux":
                    subprocess.check_call(["xdg-open", url])
                elif platform.system() == "Darwin":
                    subprocess.check_call(["open", url])
                else:
                    msg = "Unexpected platform"
                    raise Exception(msg)
            except Exception:
                logger.debug("Could not open URL")

    async def listen(self,**_) -> Coroutine[Any, Any, None]:
        if self.path:
            GUIClient.open_file(self.path)
        idmap = await EventMaster.get_instance().wait_for_identified_client("__GUI__",self.id)
        self.sid = idmap["sid"]
