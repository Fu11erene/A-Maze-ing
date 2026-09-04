from enum import Enum


class FillStatus(Enum):
    """
    盤面がどの要素で埋められているかを指定する型
    """
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


type Board = list[list[FillStatus]]
"""
迷路の盤面を定義する型
"""
type Coordinate = tuple[int, int]
"""
座標を定義する型
[0] - x座標
[1] - y座標
"""
