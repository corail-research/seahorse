from coliseum.game.game_state import GameState


class Master():

    def __init__(self,
                 name: str,
                 game_state: GameState,
                 log_file: str
                 ) -> None:
        self.name = name
        self.game_state = game_state
        self.log_file = log_file

    def play(self):
        pass

    def update_json(self):
        pass

    def get_name(self):
        pass

    def get_game_state(self):
        pass

    def get_json_path(self):
        pass

    def update_game_state(self):
        pass
