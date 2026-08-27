#!/bin/usr/env python3

from src.parser import arg_parse
from src.mazegen import MazeGenerator


def main() -> None:
    config = arg_parse()
    print(config)
    maze_gen = MazeGenerator(config=config)
    maze_gen.generate_data()
    maze_gen.print_board()
    maze_gen.generate_output()


if __name__ == "__main__":
    # try:
    main()
    # except Exception as e:
    #     print(e)
    #     exit(1)
