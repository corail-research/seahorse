import builtins
import json
import os
import random
import time

from seahorse.game.io_stream import EventSlave


class StateRecorder(EventSlave):
    """

    Records game state data received through events to a JSON file.

    This class capture and persist game state data, writing game steps
    and final summaries to a JSON file for analysis, replay, or debugging.

    Attributes:
        identifier (str): Unique identifier for the recorder instance.
        id (int): Object ID.
        wrapped_id (int): Copy of object ID for consistency.
        sid (str | None): Session ID (None until connected).
        filepath (str): Path to the JSON file where data is recorded.
    """

    def __init__(self) -> None:
        """
        Initializes the StateRecorder with unique identifier and event handlers
        for 'play' and 'done' events.
        """
        super().__init__()
        self.identifier = "__REC__"+str(int(
            time.time()*1000000-random.randint(1, 1000000)
        ))
        self.id = builtins.id(self)
        self.wrapped_id = self.id
        self.sid = None

        self.activate(self.identifier)

        self.filepath = self.identifier + ".json"
        # Initialize file if needed
        if (not os.path.exists(self.filepath)
                or os.path.getsize(self.filepath) == 0):
            with open(self.filepath, "w") as f:
                json.dump({"steps": [], "final_summary": None}, f)

        @self.sio.on("play")
        def record_play(data: str):
            """
            Event handler for 'play' events.

            Args:
                data (str):
                    JSON string containing step data from the game state.
            """
            step = json.loads(data)
            self.append_step(step)

        @self.sio.on("done")
        def record_done(data: str):
            """
            Event handler for 'done' events.

            Args:
                data (str): JSON string containing final game summary.
            """
            final_summary = json.loads(data)
            self.update_final_summary(final_summary)

        @self.sio.event()
        def disconnect():
            """
            Event handler for disconnection events.
            """
            pass

    def append_step(self, step: dict):
        """
        Appends a game step to the recording JSON file.

        Args:
            step (dict): Game step data to be recorded.
        """
        with open(self.filepath, "r+") as f:
            content = json.load(f)
            content["steps"].append(step)
            f.seek(0)
            json.dump(content, f)
            f.truncate()

    def update_final_summary(self, final_summary: dict):
        """
        Updates the recording JSON file with the final game summary.

        Args:
            final_summary (dict): Final game summary data to be recorded.
        """
        with open(self.filepath, "r+") as f:
            content = json.load(f)
            content["final_summary"] = final_summary
            f.seek(0)
            json.dump(content, f)
            f.truncate()
