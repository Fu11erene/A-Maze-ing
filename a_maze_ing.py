#!/bin/usr/env python3

from src.parser import arg_parse


def main() -> None:
    config = arg_parse()
    print(config)


if __name__ == "__main__":
    main()
