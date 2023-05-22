from coliseum.game.game_layout.board import Board, Piece


class BoardTictac(Board) :
    def __init__(self, env: dict[list[int], Piece], dim: list[int]) -> None:
        super().__init__(env, dim)