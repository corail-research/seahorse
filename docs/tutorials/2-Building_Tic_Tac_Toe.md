#2 - Building your first game

## Project structure
Seahorse allows us to focus only on what's really needed for our game setup to work properly.
Only a few files are needed to define our game-specific parameters:

```
├── main.py
├── player_tictac.py
├── master_tictac.py
├── game_state_tictac.py
├── board_tictac.py
└── GUI
    └── index.html
```

## Board definition

First we need to import the metaclasses that we need in order to build a board configuration.
Luckily as a board is a common setup for a game, an abstract class is provided by the framework.

We need both [game.game_layout.board.Board](../../reference/seahorse/game/game_layout/board/) and [game.game_layout.board.Piece](../../reference/seahorse/game/game_layout/board/#seahorse.game.game_layout.board.Piece).
We also might want to import [utils.serializer.Serializable](../../reference/seahorse/serializer/) for typing purposes.

```py
import json

from seahorse.game.game_layout.board import Board, Piece
from seahorse.utils.serializer import Serializable

```

```py
class BoardTictac(Board):

    def __init__(self, env: dict[tuple[int], Piece], dim: list[int]) -> None:
        super().__init__(env, dim)

    def to_json(self) -> dict:
        return {"env":{str(x):y for x,y in self.env.items()},
                "dim":self.dimensions}

    @classmethod
    def from_json(cls, data) -> Serializable:
        d = json.loads(data)
        dd = json.loads(data)
        for x,y in d["env"].items():
            del dd["env"][x]
            dd["env"][eval(x)] = Piece.from_json(json.dumps(y))
        return cls(**dd)

```

## Describing a generic game state
We need to describe a specific state of the game in an appropriate way. To do so, we will inherit from  [game.GameState](../../reference/seahorse/game/game_state/).

```py 
import copy
import json
from math import sqrt
from typing import Optional

from board_tictac import BoardTictac
from loguru import logger
from player_tictac import PlayerTictac

from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.game.representation import Representation
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class GameStateTictac(GameState):

    def __init__(self, scores: dict, next_player: Player, players: list[Player], rep: BoardTictac, *_, **__) -> None:

        super().__init__(scores, next_player, players, rep)
        self.num_pieces = self.get_rep().get_dimensions()[0] * self.get_rep().get_dimensions()[1]

    def get_num_pieces(self) -> int:
        return self.num_pieces

```

Let's start with the first function. It determines if the current game is finished (i.e. if all the cases are full or a player has won in our cases).

```py
    def is_done(self) -> bool:

        if len(self.rep.get_env().keys()) == self.num_pieces or self.has_won():
            return True
        return False
```

We now need to implement the logic of the game, i.e. we need to determine which actions are possible.

```py
    def generate_possible_actions(self) -> set[Action]:
        list_rep = []
        current_rep = self.get_rep()
        next_player = self.get_next_player()
        for i in range(current_rep.get_dimensions()[0]):
            for j in range(current_rep.get_dimensions()[1]):
                if not current_rep.get_env().get((i, j)):
                    copy_rep = copy.deepcopy(current_rep)
                    copy_rep.get_env()[(i, j)] = Piece(piece_type=next_player.get_piece_type(), owner=next_player)
                    list_rep.append(copy.deepcopy(copy_rep))
        poss_actions = {
            Action(
                self,
                GameStateTictac(
                    self.compute_scores(valid_next_rep),
                    self.compute_next_player(),
                    self.players,
                    valid_next_rep,
                ),
            )
            for valid_next_rep in list_rep
        }
        return poss_actions
```

As for many games, a score will be involved. In tic-tac-toe, a player simply has a score of 1 if he succeeded to align three of its pieces, 0 otherwise.

```py
    def compute_scores(self, representation: Representation) -> dict[int, float]:

        scores = {}
        bound = 2.0
        for player in self.players:
            _, pieces = representation.get_pieces_player(player)
            if len(pieces) < representation.get_dimensions()[0]:
                scores[player.get_id()] = 0.0
            else:
                success = False
                env = representation.get_env()
                dim = representation.get_dimensions()[0]
                for i in range(dim):
                    counter = 0.0
                    for j in range(dim):
                        if env.get((i, j), None) and env.get((i, j), None).get_owner_id() == player.get_id():
                            counter += 1.0
                    if counter > bound:
                        scores[player.get_id()] = 1.0
                        success = True
                if success:
                    continue
                for i in range(dim):
                    counter = 0.0
                    for j in range(dim):
                        if env.get((j, i), None) and env.get((j, i), None).get_owner_id() == player.get_id():
                            counter += 1.0
                    if counter > bound:
                        scores[player.get_id()] = 1.0
                        success = True
                if success:
                    continue
                counter = 0.0
                for i in range(dim):
                    if env.get((i, i), None) and env.get((i, i), None).get_owner_id() == player.get_id():
                        counter += 1.0
                if counter > bound:
                    scores[player.get_id()] = 1.0
                    success = True
                if success:
                    continue
                counter = 0.0
                for i in range(dim):
                    if (
                        env.get((i, dim - 1 - i), None)
                        and env.get((i, dim - 1 - i), None).get_owner_id() == player.get_id()
                    ):
                        counter += 1.0
                if counter > bound:
                    scores[player.get_id()] = 1.0
                    success = True
                if success:
                    continue
                else:
                    scores[player.get_id()] = 0.0
        return scores
``` 

It is finally useful to know if a specific game state is a winning state or not.   

```py
    def has_won(self) -> bool:
        dim = self.get_num_pieces()
        env = self.rep.get_env()
        table = []
        for k in range(dim):
            table.append(
                [p.get_owner_id() for p in [env.get((i, k), None) for i in range(int(sqrt(dim)))] if p is not None]
            )
            table.append(
                [p.get_owner_id() for p in [env.get((k, i), None) for i in range(int(sqrt(dim)))] if p is not None]
            )
        table.append(
            [p.get_owner_id() for p in [env.get((i, i), None) for i in range(int(sqrt(dim)))] if p is not None]
        )
        table.append(
            [
                p.get_owner_id()
                for p in [env.get((i, int(sqrt(dim)) - i - 1), None) for i in range(int(sqrt(dim)))]
                if p is not None
            ]
        )
        for line in table:
            if len(set(line)) == 1 and len(line) == int(sqrt(dim)):
                return True
        return False
```

Others functions are also there for convenience.

```py
    def __str__(self) -> str:
        if not self.is_done():
            return super().__str__()
        return "The game is finished!"

    def to_json(self) -> dict:
        return { i:j for i,j in self.__dict__.items() if i!="_possible_actions"}

    def convert_light_action_to_action(self,data:dict) -> Action:
        position = int(data["position"])
        logger.debug(f"Converting light action {data}")
        i = position//3
        j = position%3
        logger.debug(f"{i}{j}")
        for action in self.get_possible_actions():
            if action.get_next_game_state().get_rep().get_env().get((i,j),None) is not None:
                return action
        return None
        
    @classmethod
    def from_json(cls,data:str,*,next_player:Optional[PlayerTictac]=None) -> Serializable:
        d = json.loads(data)
        return cls(**{**d,
            "scores":{int(k):v for k,v in d["scores"].items()},
            "players":[PlayerTictac.from_json(json.dumps(x)) 
                if not isinstance(x,str) 
                else next_player 
                for x in d["players"]
                ],
            "next_player":next_player,"rep":BoardTictac.from_json(json.dumps(d["rep"]))
        })

```

## Building a game master

As in every game wether it's a couple words on the back of the box or a game master, something or someone needs to dictate de rules and design a winner when the time comes.

It's the same here, we need to have an entity that can distinguish the winner from the other players at the end of the game.

```py
from collections.abc import Iterable

from seahorse.game.game_state import GameState
from seahorse.game.master import GameMaster
from seahorse.player.player import Player


class MasterTictac(GameMaster):

    def __init__(self, 
        name: str,
        initial_game_state: GameState, 
        players_iterator: Iterable[Player], 
        log_level: str, 
        port: int = 8080, 
        hostname: str = "localhost"
     ) -> None:
        super().__init__(name, initial_game_state, players_iterator, log_level, port, hostname)

    def compute_winner(self, scores: dict[int, float]) -> list[Player]:
        max_val = max(scores.values())
        players_id = [key for key in scores if scores[key] == max_val]
        winners = [player for player in self.players if player.get_id() in players_id]
        if len(winners) > 1 :
            winners = [winners[0]]
        return winners

```

## Creating your first player
We define a first class which will contain general methods useful to every type of players.

```py
import json

from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable


class PlayerTictac(Player):

    def __init__(self, piece_type: str, name: str = "bob", **kwargs) -> None:
        super().__init__(name,**kwargs)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        return self.piece_type


    def to_json(self) -> dict:
        return {i:j for i,j in self.__dict__.items() if i!="timer"}

    @classmethod
    def from_json(cls, data) -> Serializable:
        return PlayerTictac(**json.loads(data))

```

Now, we will first try to do a basic random player. 

```py

import random

from player_tictac import PlayerTictac

from seahorse.game.action import Action
from seahorse.game.game_state import GameState


class MyPlayer(PlayerTictac):
    """
    A player class for Tic Tac Toe that selects moves randomly.
    """

    def __init__(self, piece_type: str, name: str = "bob") -> None:
        """
        Initializes a new instance of the RandomPlayerTictac class.

        Args:
            piece_type (str): The type of the player's game piece.
            name (str): The name of the player.
        """
        super().__init__(piece_type, name)

    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Implements the logic of the player by randomly selecting a feasible move.

        Args:
            current_state (GameState): The current game state.
            **kwargs: Additional keyword arguments.

        Returns:
            Action: The selected action.
        """
        possible_actions = current_state.generate_possible_actions()

        return random.choice(list(possible_actions))
```

Of course more complex (and intelligent !) players are possible. To check your general understanding of the package, it would be interesting to implement an agent based on an alpha-beta algorithm.

## Bringing it all together
Now that we have all our class and methods, we can launch locally tic-tac-toe with the help of a very simple parser in a main file.

```py
import argparse
import os
from os.path import basename, splitext, dirname
import sys
from board_tictac import BoardTictac
from master_tictac import MasterTictac
from game_state_tictac import GameStateTictac
from seahorse.utils.gui_client import GUIClient

def play(player1, player2, log_level, port, gui, gui_path, address) :
    list_players = [player1, player2]
    init_scores = {player1.get_id(): 0, player2.get_id(): 0}
    init_rep = BoardTictac(env={}, dim=[3, 3])
    initial_game_state = GameStateTictac(
        scores=init_scores, next_player=player1, players=list_players, rep=init_rep)
    master = MasterTictac(
        name="Tic-Tac-Toe", initial_game_state=initial_game_state, players_iterator=list_players, log_level=log_level, port=port, hostname=address
    )
    listeners = [GUIClient(path=gui_path)]*gui
    master.record_game(listeners=listeners)

if __name__=="__main__":
    parser = argparse.ArgumentParser(
                        prog="Launcher",
                        description="What the program does",
                        epilog="Text at the bottom of help")
    parser.add_argument("list_players",nargs="*")
    args=parser.parse_args()

    list_players = vars(args).get("list_players")

    folder = dirname(list_players[0])
    sys.path.append(folder)
    player1_class = __import__(splitext(basename(list_players[0]))[0], fromlist=[None])
    folder = dirname(list_players[1])
    sys.path.append(folder)
    player2_class = __import__(splitext(basename(list_players[1]))[0], fromlist=[None])
    player1 = player1_class.MyPlayer("X", name=splitext(basename(list_players[0]))[0])
    player2 = player2_class.MyPlayer("O", name=splitext(basename(list_players[1]))[0])
    play(player1=player1, player2=player2, log_level="INFO", port=16001, gui=1, gui_path=os.path.join("GUI","index.html"), address="localhost")
```

We can duplicate our random player class in two different python files which do not have the same name. We call them player1 and player2. We can finally do the command line:

```shell
python main.py player1.py player2.py
```

Your first game is launched !
