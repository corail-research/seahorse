from abc import abstractmethod
from coliseum.game.representation import Representation
from coliseum.utils.custom_exceptions import MethodNotImplementedError


class Player:
    """
    Attributes:
        obs (Representation): representation of the game
        id_player (int): id of the player

    Class attributes:
        next_id (int): id to be assigned to the next player
    """

    next_id = 0

    def __init__(self,
                 obs: Representation
                 ) -> None:
        self.obs = obs
        self.id_player = Player.next_id
        Player.id += 1

    @abstractmethod
    def generate_action(self):
        raise MethodNotImplementedError()

    def get_id(self):
        """
        Returns:
            int: id_player
        """
        return self.id_player

    def get_obs(self):
        """
        Returns:
            Representation: obs
        """
        return self.obs

    def update_obs(self, new_rep: Representation):
        """Update the obs attribute
        Args:
            new_rep (Representation): new representation of the game
        """
        self.obs = new_rep
