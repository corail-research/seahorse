from __future__ import annotations

from coliseum.game.game_layout.board import Board, Piece


class BoardAbalone(Board):
    """
    A class representing an Abalone board.

    Attributes:
        env (dict[tuple[int], Piece]): The environment dictionary composed of pieces.
        dimensions (list[int]): The dimensions of the board.
    """

    def __init__(self, env: dict[tuple[int], Piece], dim: list[int]) -> None:
        super().__init__(env, dim)

    def __str__(self) -> str:
        """
        Return a string representation of the board.

        Returns:
            str: The string representation of the board.
        """
        dim = self.get_dimensions()
        to_print = ""
        for i in range(dim[0]):
            for j in range(dim[1]):
                if self.get_env().get((i, j), -1) != -1:
                    to_print += (
                        str(self.get_env().get((i, j)).get_type()) + " "
                    )
                else:
                    to_print += "_ "
            to_print += "\n"
        return to_print

    def nice_repr(self) -> str:
        """
        Return a nice representation of the board.

        Returns:
            str: The nice representation of the board.
        """
        grid_data = [
            [0, 0, 2, 2, 2, 2, 2, 0, 0],
            [0, 2, 2, 2, 2, 2, 2, 0, 0],
            [0, 3, 3, 2, 2, 2, 3, 3, 0],
            [3, 3, 3, 3, 3, 3, 3, 3, 0],
            [3, 3, 3, 3, 3, 3, 3, 3, 3],
            [3, 3, 3, 3, 3, 3, 3, 3, 0],
            [0, 3, 3, 1, 1, 1, 3, 3, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
        ]
        grid_data[0][6] = self.get_env().get((0,4)).get_type() if  self.get_env().get((0,4)) else 3
        grid_data[0][5] = self.get_env().get((1,3)).get_type() if  self.get_env().get((1,3)) else 3
        grid_data[0][4] = self.get_env().get((2,2)).get_type() if  self.get_env().get((2,2)) else 3
        grid_data[0][3] = self.get_env().get((3,1)).get_type() if  self.get_env().get((3,1)) else 3
        grid_data[0][2] = self.get_env().get((4,0)).get_type() if  self.get_env().get((4,0)) else 3
        grid_data[1][6] = self.get_env().get((1,5)).get_type() if  self.get_env().get((1,5)) else 3
        grid_data[1][5] = self.get_env().get((2,4)).get_type() if  self.get_env().get((2,4)) else 3
        grid_data[1][4] = self.get_env().get((3,3)).get_type() if  self.get_env().get((3,3)) else 3
        grid_data[1][3] = self.get_env().get((4,2)).get_type() if  self.get_env().get((4,2)) else 3
        grid_data[1][2] = self.get_env().get((5,1)).get_type() if  self.get_env().get((5,1)) else 3
        grid_data[1][1] = self.get_env().get((6,0)).get_type() if  self.get_env().get((6,0)) else 3
        grid_data[2][7] = self.get_env().get((2,6)).get_type() if  self.get_env().get((2,6)) else 3
        grid_data[2][6] = self.get_env().get((3,5)).get_type() if  self.get_env().get((3,5)) else 3
        grid_data[2][5] = self.get_env().get((4,4)).get_type() if  self.get_env().get((4,4)) else 3
        grid_data[2][4] = self.get_env().get((5,3)).get_type() if  self.get_env().get((5,3)) else 3
        grid_data[2][3] = self.get_env().get((6,2)).get_type() if  self.get_env().get((6,2)) else 3
        grid_data[2][2] = self.get_env().get((7,1)).get_type() if  self.get_env().get((7,1)) else 3
        grid_data[2][1] = self.get_env().get((8,0)).get_type() if  self.get_env().get((8,0)) else 3
        grid_data[3][7] = self.get_env().get((3,7)).get_type() if  self.get_env().get((3,7)) else 3
        grid_data[3][6] = self.get_env().get((4,6)).get_type() if  self.get_env().get((4,6)) else 3
        grid_data[3][5] = self.get_env().get((5,5)).get_type() if  self.get_env().get((5,5)) else 3
        grid_data[3][4] = self.get_env().get((6,4)).get_type() if  self.get_env().get((6,4)) else 3
        grid_data[3][3] = self.get_env().get((7,3)).get_type() if  self.get_env().get((7,3)) else 3
        grid_data[3][2] = self.get_env().get((8,2)).get_type() if  self.get_env().get((8,2)) else 3
        grid_data[3][1] = self.get_env().get((9,1)).get_type() if  self.get_env().get((9,1)) else 3
        grid_data[4][8] = self.get_env().get((4,8)).get_type() if  self.get_env().get((4,8)) else 3
        grid_data[4][7] = self.get_env().get((5,7)).get_type() if  self.get_env().get((5,7)) else 3
        grid_data[4][6] = self.get_env().get((6,6)).get_type() if  self.get_env().get((6,6)) else 3
        grid_data[4][5] = self.get_env().get((7,5)).get_type() if  self.get_env().get((7,5)) else 3
        grid_data[4][4] = self.get_env().get((8,4)).get_type() if  self.get_env().get((8,4)) else 3
        grid_data[4][3] = self.get_env().get((9,3)).get_type() if  self.get_env().get((9,3)) else 3
        grid_data[5][7] = self.get_env().get((6,8)).get_type() if  self.get_env().get((6,8)) else 3
        grid_data[5][6] = self.get_env().get((7,7)).get_type() if  self.get_env().get((7,7)) else 3
        grid_data[5][5] = self.get_env().get((8,6)).get_type() if  self.get_env().get((8,6)) else 3
        grid_data[5][4] = self.get_env().get((9,5)).get_type() if  self.get_env().get((9,5)) else 3
        grid_data[6][7] = self.get_env().get((8,8)).get_type() if  self.get_env().get((8,8)) else 3
        grid_data[6][6] = self.get_env().get((9,7)).get_type() if  self.get_env().get((9,7)) else 3
        grid_data[5][3] = self.get_env().get((10,4)).get_type() if  self.get_env().get((10,4)) else 3
        grid_data[5][2] = self.get_env().get((11,3)).get_type() if  self.get_env().get((11,3)) else 3
        grid_data[5][1] = self.get_env().get((12,2)).get_type() if  self.get_env().get((12,2)) else 3
        grid_data[5][0] = self.get_env().get((13,1)).get_type() if  self.get_env().get((13,1)) else 3
        grid_data[4][2] = self.get_env().get((10,2)).get_type() if  self.get_env().get((10,2)) else 3
        grid_data[4][1] = self.get_env().get((11,1)).get_type() if  self.get_env().get((11,1)) else 3
        grid_data[4][0] = self.get_env().get((12,0)).get_type() if  self.get_env().get((12,0)) else 3
        grid_data[6][5] = self.get_env().get((10,6)).get_type() if  self.get_env().get((10,6)) else 3
        grid_data[6][4] = self.get_env().get((11,5)).get_type() if  self.get_env().get((11,5)) else 3
        grid_data[6][3] = self.get_env().get((12,4)).get_type() if  self.get_env().get((12,4)) else 3
        grid_data[6][2] = self.get_env().get((13,3)).get_type() if  self.get_env().get((13,3)) else 3
        grid_data[6][1] = self.get_env().get((14,2)).get_type() if  self.get_env().get((14,2)) else 3
        grid_data[7][6] = self.get_env().get((10,8)).get_type() if  self.get_env().get((10,8)) else 3
        grid_data[7][5] = self.get_env().get((11,7)).get_type() if  self.get_env().get((11,7)) else 3
        grid_data[7][4] = self.get_env().get((12,6)).get_type() if  self.get_env().get((12,6)) else 3
        grid_data[7][3] = self.get_env().get((13,5)).get_type() if  self.get_env().get((13,5)) else 3
        grid_data[7][2] = self.get_env().get((14,4)).get_type() if  self.get_env().get((14,4)) else 3
        grid_data[7][1] = self.get_env().get((15,3)).get_type() if  self.get_env().get((15,3)) else 3
        grid_data[8][6] = self.get_env().get((12,8)).get_type() if  self.get_env().get((12,8)) else 3
        grid_data[8][5] = self.get_env().get((13,7)).get_type() if  self.get_env().get((13,7)) else 3
        grid_data[8][4] = self.get_env().get((14,6)).get_type() if  self.get_env().get((14,6)) else 3
        grid_data[8][3] = self.get_env().get((15,5)).get_type() if  self.get_env().get((15,5)) else 3
        grid_data[8][2] = self.get_env().get((16,4)).get_type() if  self.get_env().get((16,4)) else 3
        grid_data[3][0] = self.get_env().get((10,0)).get_type() if  self.get_env().get((10,0)) else 3
        string = ""
        none_value = 3
        for i in range(9):
            if i % 2 == 1:
                string += " "
            for j in range(9):
                if grid_data[i][j] == 0:
                    string += "  "
                elif grid_data[i][j] == none_value:
                    string += "_ "
                else:
                    string += str(grid_data[i][j]) + " "
            string += "\n"
        return string

    def to_json(self) -> dict:
        """
        Convert the board to a JSON-compatible dictionary.

        Returns:
            dict: The JSON representation of the board.
        """
        board = [[None for _ in range(self.dimensions[1])] for _ in range(self.dimensions[0])]
        for key, value in self.env.items():
            board[key[0]][key[1]] = [value.owner_id, value.piece_type] if value is not None else None
        return {"board": board}
