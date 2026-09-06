from ..types import FillStatus, Coordinate, Board
from .mazegen import MazeGenerator


class RecursiveMazeGenerator(MazeGenerator):
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
        self._fill_42_pattern()

        self.board[ent_y][ent_x] = FillStatus.empty
        self._dig((ent_x, ent_y))
        self.board[ent_y][ent_x] = FillStatus.entry
        self.board[ext_y * 2 + 1][ext_x * 2 + 1] = FillStatus.exit

        return self.board

    def _is_diggable(self, pos: Coordinate) -> bool:
        x, y = pos
        if self.board is None:
            raise Exception(
                "Cannot fill 42 pattern: "
                "The Board has not been initalized yet.")
        board: Board = self.board
        if x < 0 or y < 0 \
                or x >= self._ARR_WIDTH or y >= self._ARR_HEIGHT:
            return False
        return board[y][x] == FillStatus.wall

    def _dig(self, pos: Coordinate) -> None:
        """
        どちらの向きに棒を倒すのか判断する
        """
        x, y = pos
        if self.board is None:
            raise Exception()
        # while True:
            # possible_dir: dict[Direction, Coordinate] = {
            #     Direction.up: (x + 2, y),
            #     Direction.right: (x - 2, y),
            #     Direction.down: (x, y + 2),
            #     Direction.left: (x, y - 2),
            # }
        next_poss = [(x + 2, y),
                        (x - 2, y),
                        (x, y + 2),
                        (x, y - 2),]
        possible_pos: list[Coordinate] = []
        
        for value in next_poss:
            if self._is_diggable(value):
                possible_pos.append(value)
        if len(possible_pos) == 0:
            print("Dead end. Returning...")
            return
        # ランダムにnext_possをシャッフルする
        for new_pos in next_poss:
            if self._is_diggable(new_pos):
                new_x, new_y = new_pos
                self.board[int((y + new_y) / 2)
                           ][int((x + new_x) / 2)] = FillStatus.empty
                self.board[new_y][new_x] = FillStatus.empty
                self._dig(new_pos)
