#!/bin/usr/env python3

from src.mazegen import MazeGenerator
from src.visualizer import visualize


def main() -> None:
    try:
        maze_gen = MazeGenerator()
        visualize(maze_gen)
    except ValueError as e:
        print(f"{e.__class__.__name__}: {e}")


if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except Exception as e:
    #     print(f"{e.__class__.__name__}: e")
raise SystemExit(1)
