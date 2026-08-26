import random
from ..parser import Config

type Board = list[list[bool]]
"""
迷路の盤面を定義する型
"""


class Direction[Enum]:
    up = 1
    right = 2
    down = 4
    left = 8


"""
方向を決定する型
"""

# 4方向についてのenumを生成する


class MazeGenerator:
    """
    迷路を生成するジェネレーター
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        random.seed(config.seed)

    @classmethod
    def _decide_stick(cls, x: int, y: int, board: Board) -> None:
        """
        どちらの向きに棒を倒すのか判断する
        """
        print("x:", x, "y:", y)
        possible_dir: dict[int, bool] = {
            Direction.up: False,
            Direction.right: True,
            Direction.down: True,
            Direction.left: True,
        }
        # up, down, left, right = False, True, True, True
        if y == 2:
            possible_dir[Direction.up] = True
        if board[y][x + 1]:
            possible_dir[Direction.right] = False
        if board[y][x - 1]:
            possible_dir[Direction.left] = False

        possible_dirs = 0
        for _, value in possible_dir.items():
            if value:
                possible_dirs += 1
        dir = random.randint(0, possible_dirs - 1)
        di = 0
        for key, value in possible_dir.items():
            if value:
                if di == dir:
                    cls._take_down_stick(x, y, board, key)
                    return
                else:
                    di += 1

    @classmethod
    def _take_down_stick(cls, x: int, y: int, board: Board, direction: int) -> None:
        """
        棒を実際に倒す処理
        """
        # 倒す向きの候補を現在何行目であるのかによって判断する

        #   1行目なら上下左右
        #   2行目...最後なら下と左右、ただし四方を壁に囲われて使わないマスができないようにする
        #
        if direction == Direction.up:
            print("up")
            board[y - 1][x] = True
        elif direction == Direction.down:
            print("down")
            board[y + 1][x] = True
        elif direction == Direction.left:
            print("left")
            board[y][x - 1] = True
        elif direction == Direction.right:
            print("right")
            board[y][x + 1] = True
        else:
            raise ValueError("Unknown direction: got", direction)

    def _generate_board(self) -> Board:
        WIDTH = self.config.width * 2 + 1
        HEIGHT = self.config.height * 2 + 1
        board = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if y == 0 or y == HEIGHT - 1 or x == 0 or x == WIDTH - 1:
                    board[y][x] = True
                elif y % 2 == 0 and x % 2 == 0:
                    board[y][x] = True
                    self._decide_stick(x, y, board)

        return board

    @classmethod
    def _print_board(cls, board: Board):
        for row in board:
            for cell in row:
                if cell is True:
                    print("0", end="")
                else:
                    print(" ", end="")

            print()

    def generate_maze_data(self):
        """
        迷路を生成する
        """

        board = self._generate_board()
        MazeGenerator._print_board(board)
