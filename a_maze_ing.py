#!/bin/usr/env python3

from src.parser import arg_parse
from src.mazegen import MazeGenerator


def main() -> None:
    config = arg_parse()
    print(config)
    generator = MazeGenerator(config=config)
    generator.generate_maze_data()


if __name__ == "__main__":
    main()
