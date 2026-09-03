from ..parser import Config
import random
from enum import Enum
from typing import Optional
from collections import deque

type Board = list[list[FillStatus]]
"""
迷路の盤面を定義する型
"""


class FillStatus(Enum):
    empty = 0
    wall = 1
    wall_42 = 2
    entry = 3
    exit = 4


class Direction(Enum):
    """
    方向を決定する型
    """
    up = 1
    right = 2
    down = 4
    left = 8


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
        self._ARR_WIDTH = self.config.width * 2 + 1
        self._ARR_HEIGHT = self.config.height * 2 + 1
        self.path: Optional[set[tuple[int, int]]] = None
        self.show_path = False
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
        if board[y + 1][x] is not FillStatus.empty:
            possible_dir[Direction.down] = False
        if board[y - 1][x] is not FillStatus.empty:
            possible_dir[Direction.up] = False

        possible_dirs = 0
        for _, value in possible_dir.items():
            if value:
                possible_dirs += 1
        if possible_dirs == 0:
            print("Exception: No directions to dig. Skipping.")
            return
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
        dead_ends = []
        for y in range(1, self._ARR_HEIGHT, 2):
            for x in range(1, self._ARR_WIDTH, 2):
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
        for x, y in self._dead_ends(board):
            candidates = []
            for wx, wy, nx, ny in (
                (x, y - 1, x, y - 2),
                (x + 1, y, x + 2, y),
                (x, y + 1, x, y + 2),
                (x - 1, y, x - 2, y),
            ):
                if (1 <= nx <= self._ARR_WIDTH - 2
                        and 1 <= ny <= self._ARR_HEIGHT - 2
                        and board[wy][wx] is not FillStatus.empty):
                    candidates.append((wx, wy))
            if candidates:
                wx, wy = random.choice(candidates)
                board[wy][wx] = FillStatus.empty

    def _fill_42_pattern(self) -> None:
        C_WIDTH, C_HEIGHT = self.config.width, self.config.height
        MID_X = C_WIDTH + C_WIDTH % 2 - 1
        MID_Y = C_HEIGHT + C_HEIGHT % 2 - 1
        board = self.board

        if self.config.width <= 10 or self.config.height <= 8:
            return
        elif board is None:
            raise Exception(
                "Cannot fill 42 pattern: "
                "The Board has not been initalized yet.")

        for (x, y) in (
            (MID_X - 6, MID_Y - 4),
            (MID_X + 2, MID_Y - 4),
            (MID_X + 4, MID_Y - 4),
            (MID_X + 6, MID_Y - 4),
            (MID_X - 6, MID_Y - 2),
            (MID_X + 6, MID_Y - 2),
            (MID_X - 6, MID_Y - 0),
            (MID_X - 4, MID_Y - 0),
            (MID_X - 2, MID_Y - 0),
            (MID_X + 2, MID_Y - 0),
            (MID_X + 4, MID_Y - 0),
            (MID_X + 6, MID_Y - 0),
            (MID_X - 2, MID_Y + 2),
            (MID_X + 2, MID_Y + 2),
            (MID_X - 2, MID_Y + 4),
            (MID_X + 2, MID_Y + 4),
            (MID_X + 4, MID_Y + 4),
            (MID_X + 6, MID_Y + 4),
        ):
            for ay in range(-1, 2):
                for ax in range(-1, 2):
                    board[y + ay][x + ax] = FillStatus.wall_42
            board[y][x] = FillStatus.empty

    def _generate_board(self) -> Board:
        """
        棒倒し法でボードを生成する
        """
        WIDTH = self._ARR_WIDTH
        HEIGHT = self._ARR_HEIGHT
        ent_x, ent_y = self.config.entry
        ext_x, ext_y = self.config.exit
        board: Board = [
            [FillStatus.empty for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.board = board
        # self._fill_42_pattern()

        board[ent_y * 2 + 1][ent_x * 2 + 1] = FillStatus.entry
        board[ext_y * 2 + 1][ext_x * 2 + 1] = FillStatus.exit

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if board[y][x] is FillStatus.wall_42:
                    continue
                elif y == 0 or y == HEIGHT - 1 or x == 0 or x == WIDTH - 1:
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
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if (self.path is not None and
                        self.show_path and (y, x) in self.path):
                    print(self.wall_list[3], end="")
                    continue

                match cell:
                    case FillStatus.entry:
                        print(self.wall_list[1], end="")
                    case FillStatus.exit:
                        print(self.wall_list[2], end="")
                    case FillStatus.wall:
                        print(self.wall_list[self.wall_colour_offset], end="")
                    case FillStatus.wall_42:
                        print("42", end="")
                    case _:
                        print("  ", end="")

            print()

    def solve_with_bfs(self) -> Optional[set[tuple[int, int]]]:
        """
        BFSで入口から出口までの最短経路を求め、通過するマスの
        (y, x) 座標集合を返す。到達できない場合は None を返す。
        """
        board = self.board
        start = self.config.entry
        goal = self.config.exit
        rows = self.config.height * 2 + 1
        cols = self.config.width * 2 + 1

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        visited = [[False] * cols for _ in range(rows)]
        prev: list[list[Optional[tuple[int, int]]]] = [
            [None] * cols for _ in range(rows)]
        queue: deque[tuple[int, int]] = deque()
        start_y, start_x = start[1] * 2 + 1, start[0] * 2 + 1
        goal_y, goal_x = goal[1] * 2 + 1, goal[0] * 2 + 1
        visited[start_y][start_x] = True
        queue.append((start_y, start_x))

        while queue:
            y, x = queue.popleft()
            if (y, x) == (goal_y, goal_x):
                path: set[tuple[int, int]] = set()
                cur: Optional[tuple[int, int]] = (y, x)
                while cur is not None:
                    path.add(cur)
                    cur = prev[cur[0]][cur[1]]
                path.discard((start_y, start_x))
                path.discard((y, x))
                return path

            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    if (board is not None and board[ny][nx] != FillStatus.wall
                            and not visited[ny][nx]):
                        visited[ny][nx] = True
                        prev[ny][nx] = (y, x)
                        queue.append((ny, nx))

        return None

    def toggle_path(self) -> None:
        """
        最短経路の表示・非表示を切り替えて盤面を再描画する
        """
        if self.path is None:
            self.path = self.solve_with_bfs()
        self.show_path = not self.show_path
        self.print_board()

    def _generate_outstr(self) -> str:
        """
        課題で求められている迷路の部分についてのファイルの文字列を構成する
        """
        if self.board is None:
            raise Exception(
                "Cannot generate outstr: "
                "The Board has not been initalized yet.")
        result = ""
        for y in range(1, self._ARR_HEIGHT - 1, 2):
            for x in range(1, self._ARR_WIDTH - 1, 2):
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
        self.path = None
        self.show_path = False

    def rotate_wall_colour(self) -> None:
        self.wall_colour_offset = (
            self.wall_colour_offset + 2) % len(self.wall_list)
        self.print_board()
