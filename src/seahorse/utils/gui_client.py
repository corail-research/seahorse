import builtins
import os
import subprocess
from typing import Any, Coroutine, Optional

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
                subprocess.call(["open", url])
            except Exception:
                logger.debug("Could not open URL")

    async def listen(self,**_) -> Coroutine[Any, Any, None]:
        if self.path:
            GUIClient.open_file(self.path)
        idmap = await EventMaster.get_instance().wait_for_identified_client("__GUI__",self.id)
        self.sid = idmap["sid"]
