import argparse
import sys
from pydantic import BaseModel, validator, ValidationError, conint


class Config(BaseModel):
    width: conint(ge=0)
    height: conint(ge=0)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool

    @classmethod
    def is_valid_coordinate(cls, x: int, y: int, width: int, height: int) -> bool:
        return (x >= 0 and x <= width - 1) and (y >= 0 and y <= height - 1)

    @validator("width")
    def width_validate(cls, width: str) -> int:
        try:
            return int(width)
        except ValueError:
            ValueError()

    @validator("height")
    def height_validate(cls, height: str) -> int:
        try:
            return int(height)
        except ValueError:
            ValueError()

    @validator("entry", pre=True)
    def entry_validate(cls, entry: str, values: dict) -> tuple[int, int]:
        try:
            x, y = (int(point) for point in entry.split(","))

            if cls.is_valid_coordinate(x, y, values["width"], values["height"]):
                return (x, y)
            else:
                raise ValueError()
        except ValueError:
            raise ValueError()

    @validator("exit", pre=True)
    def exit_validate(cls, exit: str, values: dict) -> tuple[int, int]:
        try:
            x, y = (int(point) for point in exit.split(","))

            if cls.is_valid_coordinate(x, y, values["width"], values["height"]) and (x, y) != values["entry"]:
                return (x, y)
            else:
                raise ValueError()
        except ValueError:
            raise ValueError()


def convert_dict(entry_list: list[str]) -> dict[str, str]:
    entry_dict = {}
    for entry in entry_list:
        key, value = entry.split("=")
        entry_dict.update({key: value})
    return entry_dict


def arg_parse() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument("filename", type=open, help="設定ファイル")

    try:
        args = parser.parse_args()
        entry_list = [entry.strip().lower()
                      for entry in args.filename.readlines()
                      if entry[0] != "#" and entry[0] != " "]
        entry_dict = convert_dict(entry_list)
        config = Config(**entry_dict)
        print(entry_dict)
        print(config)
    except (Exception, ValidationError) as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
