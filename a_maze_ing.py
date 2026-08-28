#!/bin/usr/env python3

from src.parser import arg_parse
from src.mazegen import MazeGenerator
from src.visualizer import visualize


def main() -> None:
    config = arg_parse()
    print(config)
    maze_gen = MazeGenerator(config=config)
    visualize(maze_gen)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        exit(1)
