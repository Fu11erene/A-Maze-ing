from ..parser import Config


type Board = list[list[bool]]
"""
迷路の盤面を定義する型
"""


class MazeGenerator:
    def __init__(self, config: Config) -> None:
        self.config = config

    def _init_board(self) -> Board:
        WIDTH = self.config.width * 2 + 1
        HEIGHT = self.config.height * 2 + 1
        board = [[False] * (WIDTH)] * (HEIGHT)
        board = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]

        print("W:", WIDTH)
        print("H:", HEIGHT)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if y == 0 or y == HEIGHT - 1 or x == 0 or x == WIDTH - 1 \
                        or (y % 2 == 0 and x % 2 == 0):
                    board[y][x] = True
                else:
                    board[y][x] = False

        return board

    @classmethod
    def _print_board(cls, board: Board):
        for y, row in enumerate(board):
            print(y, end=": ")
            for cell in row:
                if cell is True:
                    print("T", end="")
                else:
                    print(" ", end="")

            print()

    def generate_maze_data(self):
        """
        迷路を生成する
        """

        board = self._init_board()
        MazeGenerator._print_board(board)
