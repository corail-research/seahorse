from coliseum.game.representation import Representation


class Player:
    id_player: int
    obs: Representation

    def __init__(self) -> None:
        pass

    def generate_action(self):
        pass

    def get_id(self):
        pass

    def get_obs(self):
        pass

    def update_obs(self, new_rep: Representation):
        pass
