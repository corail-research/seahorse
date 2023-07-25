import json
from websocket import create_connection
from seahorse.examples.abalone.player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.serializer import Serializable

class MyPlayer(PlayerAbalone):

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        super().__init__(piece_type, name)
        self.websocket = create_connection("ws://localhost:8080")
        self.player_type = "human"

    def compute_action(self, current_state: GameState) -> Action:
        print("Waiting for message")
        while True:
            msg = self.websocket.recv()
            # convert msg to dict
            data = json.loads(msg)
            print("Received message", data)
            print(self.piece_type)
            if data["type"] == self.piece_type:
                action = current_state.convert_light_action_to_action(data["from"], data["to"])
                print("Sending action", action)
                if action is None:
                    self.websocket.send(json.dumps({"type": "error", "message": "Invalid action"}))
                else:
                    break

        return action
    
    def toJson(self) -> str:
        return json.dumps({ i:j for i,j in self.__dict__.items() if i!="websocket"},default=lambda x:x.toJson() if isinstance(x,Serializable) else None)

    @classmethod
    def fromJson(cls, data) -> Serializable:
        return PlayerAbalone(**json.loads(data))