from ..parser import Config
import random
from enum import Enum
from typing import Optional

type Board = list[list[FillStatus]]
"""
迷路の盤面を定義する型
"""


class FillStatus(Enum):
    empty = 0
    wall = 1
    wall_42 = 2


class Direction(Enum):
    """
    方向を決定する型
    """
    up = 1
    right = 2
    down = 4
    left = 8


# 4方向についてのenumを生成するs


class MazeGenerator:
    """
    迷路を生成するジェネレーター
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.board: Optional[Board] = None
        self.wall_colour_offset = 0
        self.wall_list = ["██", "\033[31m██\033[0m", "\033[32m██\033[0m",
                          "\033[34m██\033[0m", "\033[33m██\033[0m"]
        random.seed(config.seed)

    @classmethod
    def _decide_stick(cls, x: int, y: int, board: Board) -> None:
        """
        どちらの向きに棒を倒すのか判断する
        """
        possible_dir: dict[Direction, bool] = {
            Direction.up: False,
            Direction.right: True,
            Direction.down: True,
            Direction.left: True,
        }
        if y == 2:
            possible_dir[Direction.up] = True
        if board[y][x + 1] is not FillStatus.empty:
            possible_dir[Direction.right] = False
        if board[y][x - 1] is not FillStatus.empty:
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

    @staticmethod
    def _take_down_stick(x: int, y: int, board: Board, direction: Direction
                         ) -> None:
        """
        棒を実際に倒す処理

        - 1行目なら上下左右
        - 2行目以降なら下と左右、ただし四方を壁に囲われて使わないマスができないようにする
        """
        if direction == Direction.up:
            board[y - 1][x] = FillStatus.wall
        elif direction == Direction.down:
            board[y + 1][x] = FillStatus.wall
        elif direction == Direction.left:
            board[y][x - 1] = FillStatus.wall
        elif direction == Direction.right:
            board[y][x + 1] = FillStatus.wall
        else:
            raise ValueError("Unknown direction: got", direction)

    def _dead_ends(self, board: Board) -> list[tuple[int, int]]:
        """
        行き止まりになっているセル(開口部が1つしかないセル)の座標一覧を返す
        """
        WIDTH = self.config.width * 2 + 1
        HEIGHT = self.config.height * 2 + 1
        dead_ends = []
        for y in range(1, HEIGHT, 2):
            for x in range(1, WIDTH, 2):
                walls = (board[y - 1][x], board[y][x + 1],
                         board[y + 1][x], board[y][x - 1])
                if walls.count(FillStatus.empty) == 1:
                    dead_ends.append((x, y))
        return dead_ends

    def _braid(self, board: Board) -> None:
        """
        行き止まりのセルについて、外周に面していない壁を1つ取り除いて
        隣接するセルと繋げることで、迷路からループを作り行き止まりをなくす
        """
        WIDTH = self.config.width * 2 + 1
        HEIGHT = self.config.height * 2 + 1
        for x, y in self._dead_ends(board):
            candidates = []
            for wx, wy, nx, ny in (
                (x, y - 1, x, y - 2),
                (x + 1, y, x + 2, y),
                (x, y + 1, x, y + 2),
                (x - 1, y, x - 2, y),
            ):
                if (1 <= nx <= WIDTH - 2 and 1 <= ny <= HEIGHT - 2
                        and board[wy][wx] is not FillStatus.empty):
                    candidates.append((wx, wy))
            if candidates:
                wx, wy = random.choice(candidates)
                board[wy][wx] = FillStatus.empty

    def _generate_board(self) -> Board:
        """
        棒倒し法でボードを生成する
        """
        WIDTH = self.config.width * 2 + 1
        HEIGHT = self.config.height * 2 + 1
        board: Board = [
            [FillStatus.empty for _ in range(WIDTH)] for _ in range(HEIGHT)]

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if y == 0 or y == HEIGHT - 1 or x == 0 or x == WIDTH - 1:
                    board[y][x] = FillStatus.wall
                elif y % 2 == 0 and x % 2 == 0:
                    board[y][x] = FillStatus.wall
                    self._decide_stick(x, y, board)

        return board

    def print_board(self) -> None:
        """
        盤面を出力
        """
        if self.board is None:
            raise Exception("The Board has not been initalized yet.")
        for row in self.board:
            for cell in row:
                match cell:
                    case FillStatus.wall:
                        print(self.wall_list[self.wall_colour_offset], end="")
                    case FillStatus.wall_42:
                        print("42", end="")
                    case _:
                        print("  ", end="")

            print()

    def _generate_outstr(self) -> str:
        """
        課題で求められている迷路の部分についてのファイルの文字列を構成する
        """
        if self.board is None:
            raise Exception(
                "Cannot generate outstr: "
                "The Board has not been initalized yet.")
        result = ""
        WIDTH = self.config.width * 2 + 1
        HEIGHT = self.config.height * 2 + 1
        for y in range(1, HEIGHT, 2):
            for x in range(1, WIDTH, 2):
                # current_cell = self.board[row][col]
                north = self.board[y-1][x] is not FillStatus.empty
                east = self.board[y][x+1] is not FillStatus.empty
                south = self.board[y+1][x] is not FillStatus.empty
                west = self.board[y][x-1] is not FillStatus.empty
                current_digit = "%x" % (
                    west * 8 + south * 4 + east * 2 + north)
                result += current_digit
            result += "\n"
        return result

    def generate_output(self) -> None:
        outstr = self._generate_outstr()
        ent_x, ent_y = self.config.entry
        ext_x, ext_y = self.config.exit
        with open(self.config.output_file, mode="w") as f:
            f.write(outstr + "\n")
            f.write(f"{ent_x},{ent_y}")
            f.write("\n")
            f.write(f"{ext_x},{ext_y}")
            f.write("\n")

    def generate_data(self) -> None:
        """
        迷路を生成する
        """
        self.board = self._generate_board()
        if not self.config.perfect:
            self._braid(self.board)

    def rotate_wall_colour(self) -> None:
        self.wall_colour_offset = (
            self.wall_colour_offset + 1) % len(self.wall_list)
        self.print_board()
