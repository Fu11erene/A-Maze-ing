import random
import sys
from collections import deque
from typing import Optional
from ..parser import Config
from ..types import Board, Coordinate, Direction, FillStatus
from ..errors import BoardUninitializedError, PatternConflictError


RECURSION_LIMIT = 10000
FT_PATTERNS = ((- 6, - 4), (+ 2, - 4),
               (+ 4, - 4), (+ 6, - 4),
               (- 6, - 2), (+ 6, - 2),
               (- 6, - 0), (- 4, - 0),
               (- 2, - 0), (+ 2, - 0),
               (+ 4, - 0), (+ 6, - 0),
               (- 2, + 2), (+ 2, + 2),
               (- 2, + 4), (+ 2, + 4),
               (+ 4, + 4), (+ 6, + 4))


class MazeGenerator:
    """
    迷路を生成するジェネレーター
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.board: Optional[Board] = None
        self.wall_colour_offset = 0
        # 壁の色は白、赤、緑、青、茶(42のterminal環境では)
        self.wall_list = ["██", "\033[31m██\033[0m", "\033[32m██\033[0m",
                          "\033[34m██\033[0m", "\033[33m██\033[0m"]
        self._ARR_WIDTH = self.config.width * 2 + 1
        self._ARR_HEIGHT = self.config.height * 2 + 1
        self.path: Optional[set[Coordinate]] = None
        self.show_path = False
        self.path_direction = ""
        random.seed(config.seed)
        if sys.getrecursionlimit() < RECURSION_LIMIT:
            sys.setrecursionlimit(RECURSION_LIMIT)

    def _dead_ends(self, board: Board) -> list[Coordinate]:
        """
        行き止まりになっているセル(開口部が1つしかないセル)の座標一覧を返す
        """
        dead_ends: list[Coordinate] = []
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
            candidates: list[Coordinate] = []
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

    def is_42_renderable(self) -> bool:
        return self.config.width > 10 and self.config.height > 8

    def _fill_42_pattern(self) -> None:
        C_WIDTH, C_HEIGHT = self.config.width, self.config.height
        MID_X = C_WIDTH + C_WIDTH % 2 - 1
        MID_Y = C_HEIGHT + C_HEIGHT % 2 - 1
        board = self.board

        if board is None:
            raise BoardUninitializedError(
                "Cannot fill 42 pattern: "
                "The Board has not been initalized yet.")
        elif not self.is_42_renderable():
            return

        for (dx, dy) in FT_PATTERNS:
            x, y = (MID_X + dx, MID_Y + dy)
            if board[y][x] is not FillStatus.wall:
                raise PatternConflictError("Entry or/and exit conflicts with the 42 pattern.")
            for ay in range(-1, 2):
                for ax in range(-1, 2):
                    board[y + ay][x + ax] = FillStatus.wall_42
            board[y][x] = FillStatus.wall_42_empty

    def _reconstruct_path(
        self,
        start: Coordinate,
        goal: Coordinate,
        prev_cordinate: list[list[Optional[Coordinate]]],
    ) -> set[Coordinate]:
        """
        goal から prev_cordinate を辿って start までの経路座標集合を復元する。
        start と goal 自身は含めない。
        """
        path: set[Coordinate] = set()
        cur: Optional[Coordinate] = goal
        while cur is not None:
            path.add(cur)
            cur = prev_cordinate[cur[1]][cur[0]]
        path.discard(start)
        path.discard(goal)
        return path

    def _compute_reversed_directions(
        self,
        start: Coordinate,
        goal: Coordinate,
        prev_cordinate: list[list[Optional[Coordinate]]],
    ) -> str:
        """
        goal から start に向かって prev_cordinate を辿りながら、
        各ステップの移動方向(N/S/E/W)を連結した文字列を返す。
        """
        directions = ""
        cur = goal
        while cur != start:
            cur_x, cur_y = cur
            prev = prev_cordinate[cur_y][cur_x]
            if prev is None:
                raise ValueError("Invalid Maze")
            prev_x, prev_y = prev
            if (prev_x + 1, prev_y) == (cur_x, cur_y):
                directions += "E"
            elif (prev_x - 1, prev_y) == (cur_x, cur_y):
                directions += "W"
            if (prev_x, prev_y + 1) == (cur_x, cur_y):
                directions += "S"
            if (prev_x, prev_y - 1) == (cur_x, cur_y):
                directions += "N"
            cur = (prev_x, prev_y)
        return directions

    def _solve_with_bfs(self) -> tuple[Optional[set[Coordinate]], str]:
        """
        BFSで入口から出口までの最短経路を求め、通過するマスの
        (x, y) 座標集合を返す。到達できない場合は None を返す。
        """
        board = self.board
        start = self.config.entry
        goal = self.config.exit
        HEIGHT = self._ARR_HEIGHT
        WIDTH = self._ARR_WIDTH

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        visited = [[False] * WIDTH for _ in range(HEIGHT)]
        prev_cordinate: list[list[Optional[Coordinate]]] = [
            [None] * WIDTH for _ in range(HEIGHT)]
        queue: deque[Coordinate] = deque()
        start_x, start_y = start[0] * 2 + 1, start[1] * 2 + 1
        goal_x, goal_y = goal[0] * 2 + 1, goal[1] * 2 + 1
        visited[start_y][start_x] = True
        queue.append((start_x, start_y))

        while queue:
            x, y = queue.popleft()
            if (x, y) == (goal_x, goal_y):
                path = self._reconstruct_path(
                    (start_x, start_y), (x, y), prev_cordinate)
                reversed_path_direction = self._compute_reversed_directions(
                    (start_x, start_y), (goal_x, goal_y), prev_cordinate)
                path_direction = reversed_path_direction[::-1]
                return (path, path_direction)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= ny < HEIGHT and 0 <= nx < WIDTH:
                    if (board is not None
                            and board[ny][nx] != FillStatus.wall
                            and board[ny][nx] != FillStatus.wall_42
                            and not visited[ny][nx]):
                        visited[ny][nx] = True
                        prev_cordinate[ny][nx] = (x, y)
                        queue.append((nx, ny))

        return None, ""

    def _clear_terminal(self) -> None:
        """
        左上にカーソルを移動して(\033[H)画面をクリア(\033[J)する
        """
        print("\033[H\033[J", end="")

    def _generate_outstr(self) -> str:
        """
        課題で求められている迷路の部分についてのファイルの文字列を構成する
        """
        if self.board is None:
            raise BoardUninitializedError(
                "Cannot generate outstr: "
                "The Board has not been initalized yet.")
        result = ""
        for y in range(1, self._ARR_HEIGHT - 1, 2):
            for x in range(1, self._ARR_WIDTH - 1, 2):
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
        """
        迷路の情報、ENTRY、EXIT、正解の経路の経路をファイルに出力する
        """
        outstr = self._generate_outstr()
        ent_x, ent_y = self.config.entry
        ext_x, ext_y = self.config.exit
        with open(self.config.output_file, mode="w") as f:
            f.write(outstr + "\n")
            f.write(f"{ent_x},{ent_y}")
            f.write("\n")
            f.write(f"{ext_x},{ext_y}")
            f.write("\n")
            f.write(self.path_direction)
            f.write("\n")

    def _generate_board(self) -> Board:
        """
        穴掘り法でボードを生成する
        """
        WIDTH = self._ARR_WIDTH
        HEIGHT = self._ARR_HEIGHT
        ent_x = self.config.entry[0] * 2 + 1
        ent_y = self.config.entry[1] * 2 + 1
        ext_x, ext_y = self.config.exit
        self.board = [
            [FillStatus.wall for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.board[ent_y][ent_x] = FillStatus.entry
        self.board[ext_y * 2 + 1][ext_x * 2 + 1] = FillStatus.exit
        self._fill_42_pattern()
        self.board[ext_y * 2 + 1][ext_x * 2 + 1] = FillStatus.wall

        self.board[ent_y][ent_x] = FillStatus.empty
        self._carve((ent_x, ent_y), None)
        self.board[ent_y][ent_x] = FillStatus.entry
        self.board[ext_y * 2 + 1][ext_x * 2 + 1] = FillStatus.exit

        return self.board

    def _is_carveable(self, pos: Coordinate) -> bool:
        x, y = pos
        if self.board is None:
            raise BoardUninitializedError(
                "Cannot fill 42 pattern: "
                "The Board has not been initalized yet.")
        board: Board = self.board
        if x < 0 or y < 0 \
                or x >= self._ARR_WIDTH or y >= self._ARR_HEIGHT:
            return False
        return board[y][x] == FillStatus.wall

    def _carve(self, pos: Coordinate, prev_dir: Optional[Direction]) -> None:
        """
        どちらの向きに棒を倒すのか判断する
        """
        x, y = pos
        if self.board is None:
            raise BoardUninitializedError(
                "Cannot fill 42 pattern: "
                "The Board has not been initalized yet.")
        possible_dir: dict[Direction, Coordinate] = {
            Direction.up: (x + 2, y),
            Direction.right: (x - 2, y),
            Direction.down: (x, y + 2),
            Direction.left: (x, y - 2),
        }
        directions = [Direction.up, Direction.right,
                      Direction.down, Direction.left]

        random.shuffle(directions)
        for dir in directions:
            new_pos = possible_dir[dir]
            if self._is_carveable(new_pos):
                new_x, new_y = new_pos
                self.board[int((y + new_y) / 2)
                           ][int((x + new_x) / 2)] = FillStatus.empty
                self.board[new_y][new_x] = FillStatus.empty
                self._carve(new_pos, dir)

    def generate_data(self) -> None:
        """
        迷路を生成する
        """

        self.board = self._generate_board()
        if not self.config.perfect:
            self._braid(self.board)
        self.path, self.path_direction = self._solve_with_bfs()
        self.show_path = False

    def _select_wall_color(self, step: int) -> int:
        """
        stepだけ次の壁の色の添字を返す
        """
        return (self.wall_colour_offset + step) % len(self.wall_list)

    def print_board(self) -> None:
        """
        盤面を出力
        """
        if self.board is None:
            raise BoardUninitializedError(
                "The Board has not been initialized yet.")
        self._clear_terminal()
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if (self.path is not None and
                        self.show_path and (x, y) in self.path):
                    print(
                        self.wall_list[self._select_wall_color(1)], end="")
                    continue

                match cell:
                    case FillStatus.entry:
                        print(
                            self.wall_list[self._select_wall_color(2)], end="")
                    case FillStatus.exit:
                        print(
                            self.wall_list[self._select_wall_color(3)], end="")
                    case FillStatus.wall:
                        print(self.wall_list[self.wall_colour_offset], end="")
                    case FillStatus.wall_42:
                        print("42", end="")
                    case FillStatus.wall_42_empty:
                        print("\\\\", end="")
                    case _:
                        print("  ", end="")

            print()

    def rotate_wall_colour(self) -> None:
        """
        壁の色を変える
        """
        self.wall_colour_offset = self._select_wall_color(1)

    def toggle_path(self) -> None:
        """
        最短経路の表示・非表示を切り替えて盤面を再描画する
        """
        self.show_path = not self.show_path
