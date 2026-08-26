from ..parser import Config


type Board = list[list[bool]]
"""
迷路の盤面を定義する型
"""


class MazeGenerator:
    """
    迷路を生成するジェネレーター
    """
    def __init__(self, config: Config) -> None:
        self.config = config

    def _generate_board(self) -> Board:
        WIDTH = self.config.width * 2 + 1
        HEIGHT = self.config.height * 2 + 1
        board = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if y == 0 or y == HEIGHT - 1 or x == 0 or x == WIDTH - 1 \
                        or (y % 2 == 0 and x % 2 == 0):
                    board[y][x] = True
                    # ここに、棒を実際に倒す処理を加える
                    # 倒す向きの候補を現在何行目であるのかによって判断する
                    #   1行目なら上下左右
                    #   2行目...最後なら下と左右、ただし四方を壁に囲われて使わないマスができないようにする
                    #
                # else:
                #     board[y][x] = False

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

        board = self._generate_board()
        MazeGenerator._print_board(board)
