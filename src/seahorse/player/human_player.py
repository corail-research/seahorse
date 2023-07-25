from websocket import create_connection
import math
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.player.player import Player



class HumanPlayer(Player):

    def __init__(self, name, port):
        super().__init__(name, port)
        self.websocket = create_connection("ws://localhost:8080")
        self.playing = True


    
    def play(self, current_state: GameState) -> Action:
        self.playing = True
        print("Waiting for message")
        while True:
            msg = self.websocket.recv()
            print(f"Received message: {msg}")
            break
        self.playing = False
        self.message = None
        return None
    

    
