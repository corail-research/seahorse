import builtins
import json
import random
import time

from seahorse.game.io_stream import EventSlave


class StateRecorder(EventSlave):
    """ An event slave that records everything state emitted by the master in a json file
    """

    def __init__(self) -> None:
        super().__init__()
        self.identifier = "__REC__"+str(int(time.time()*1000000-random.randint(1,1000000)))
        self.id = builtins.id(self)
        self.wrapped_id = self.id
        self.sid = None

        self.activate(self.identifier)
        self.recorded_content = {"steps" : [], "final_summary" : None}

        @self.sio.on("play")
        def record_play(data):
            self.recorded_content["steps"].append(json.loads(data))

        @self.sio.on("done")
        def record_done(data):
            self.recorded_content["final_summary"] = json.loads(data)

        @self.sio.event()
        def disconnect():
            with open(self.identifier+".json","w+") as f:
                f.write(json.dumps(self.recorded_content))


