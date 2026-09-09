#!/bin/usr/env python3

from mazegen import MazeGenerator, arg_parse, visualize


def main() -> None:
    try:
        config = arg_parse()
        maze_gen = MazeGenerator(config)
        visualize(maze_gen)
    except ValueError as e:
        print(f"{e.__class__.__name__}: {e}")


if __name__ == "__main__":
    main()
