import builtins
import json
import os
import random
import time

from seahorse.game.io_stream import EventSlave


class StateRecorder(EventSlave):
    """
    An event slave that records everything state emitted by the master in a json file
    """

    def __init__(self) -> None:
        super().__init__()
        self.identifier = "__REC__"+str(int(time.time()*1000000-random.randint(1,1000000)))
        self.id = builtins.id(self)
        self.wrapped_id = self.id
        self.sid = None

        self.activate(self.identifier)

        self.filepath = self.identifier + ".json"
         # Initialize file if needed
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, "w") as f:
                json.dump({"steps": [], "final_summary": None}, f)

        @self.sio.on("play")
        def record_play(data):
            step = json.loads(data)
            self.append_step(step)

        @self.sio.on("done")
        def record_done(data):
            final_summary = json.loads(data)
            self.update_final_summary(final_summary)

        @self.sio.event()
        def disconnect():
            pass

    def append_step(self, step):
        with open(self.filepath, "r+") as f:
            content = json.load(f)
            content["steps"].append(step)
            f.seek(0)
            json.dump(content, f)
            f.truncate()

    def update_final_summary(self, final_summary):
        with open(self.filepath, "r+") as f:
            content = json.load(f)
            content["final_summary"] = final_summary
            f.seek(0)
            json.dump(content, f)
            f.truncate()
