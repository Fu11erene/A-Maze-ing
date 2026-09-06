#!/bin/usr/env python3

from src.parser import arg_parse
from src.mazegen import BinaryTreeMazeGenerator, RecursiveMazeGenerator
from src.visualizer import visualize


def main() -> None:
    config = arg_parse()
    print(config)
    # maze_gen = BinaryTreeMazeGenerator(config=config)
    maze_gen = RecursiveMazeGenerator(config=config)
    visualize(maze_gen)


if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except Exception as e:
    #     print(f"{e.__class__.__name__}: e")
raise SystemExit(1)
