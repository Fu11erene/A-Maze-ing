import random
from ..types import FillStatus, Direction, Board
from .mazegen import MazeGenerator


class BinaryTreeMazeGenerator(MazeGenerator):
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
        for value in possible_dir.values():
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
