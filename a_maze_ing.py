#!/bin/usr/env python3

from src.parser import arg_parse
from src.mazegen import MazeGenerator


def main() -> None:
    config = arg_parse()
    print(config)
    generator = MazeGenerator(config=config)
    result = generator.generate_maze_data()
    generator.print_board(result)


if __name__ == "__main__":
    main()
