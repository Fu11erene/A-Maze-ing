import argparse
import sys
from pydantic import BaseModel, field_validator, ValidationError, Field
from pydantic_core.core_schema import ValidationInfo


class Config(BaseModel):
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool

    @classmethod
    def is_valid_coordinate(cls, x: int, y: int, width: int, height: int) -> bool:
        return (x >= 0 and x <= width - 1) and (y >= 0 and y <= height - 1)

    @field_validator("width", mode="before")
    @classmethod
    def width_validate(cls, width: str) -> int:
        try:
            return int(width)
        except ValueError:
            raise ValueError()

    @field_validator("height", mode="before")
    @classmethod
    def height_validate(cls, height: str) -> int:
        try:
            return int(height)
        except ValueError:
            ValueError()

    @field_validator("entry", mode="before")
    @classmethod
    def entry_validate(cls, entry: str, info: ValidationInfo) -> tuple[int, int]:
        try:
            x, y = (int(point)
                    for point in entry.split(",") if point == point.strip())

            if cls.is_valid_coordinate(x, y, info.data.get("width"), info.data.get("height")):
                return (x, y)
            else:
                raise ValueError()
        except ValueError:
            raise ValueError()

    @field_validator("exit", mode="before")
    @classmethod
    def exit_validate(cls, exit: str, info: ValidationInfo) -> tuple[int, int]:
        try:
            x, y = (int(point)
                    for point in exit.split(",") if point == point.strip())

            if cls.is_valid_coordinate(x, y, info.data.get("width"), info.data.get("height")) and (x, y) != info.data.get("entry"):
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
    except ValidationError as e:
        print(f"Invalid parameter: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
