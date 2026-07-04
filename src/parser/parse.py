import argparse
from sys import exit
from pydantic import BaseModel, field_validator, ValidationError, Field
from pydantic_core.core_schema import ValidationInfo


class KeyAlreadyExistError(Exception):
    pass


class Config(BaseModel):
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool

    @classmethod
    def assign_coordinate(cls, point: str) -> tuple[int, int]:
        try:
            x, y = (int(p)
                    for p in point.split(",") if point == point.strip())
            return (x, y)
        except ValueError:
            raise ValueError()

    @classmethod
    def entry_info_validate(cls, info: ValidationInfo) -> tuple[int, int]:
        width = info.data.get("width")
        height = info.data.get("height")
        for param in [width, height]:
            if param is None:
                raise ValueError()
        return (width, height)

    @classmethod
    def exit_info_validate(cls, info: ValidationInfo) -> tuple[int, int, tuple[int, int]]:
        width = info.data.get("width")
        height = info.data.get("height")
        entry = info.data.get("entry")
        for param in [width, height, entry]:
            if param is None:
                raise ValueError()
        return (width, height, entry)

    @classmethod
    def is_valid_coordinate(cls, x: int, y: int, width: int, height: int) -> bool:
        return (x >= 0 and x <= width - 1) and (y >= 0 and y <= height - 1)

    @field_validator("width", mode="before")
    @classmethod
    def width_validate(cls, width: str) -> int:
        try:
            return int(width)
        except ValueError:
            raise ValueError("Invalid WIDTH")

    @field_validator("height", mode="before")
    @classmethod
    def height_validate(cls, height: str) -> int:
        try:
            return int(height)
        except ValueError:
            ValueError("Invalid HEIGHT")

    @field_validator("entry", mode="before")
    @classmethod
    def entry_validate(cls, entry: str, info: ValidationInfo) -> tuple[int, int]:
        try:
            x, y = cls.assign_coordinate(entry)
            width, height = cls.entry_info_validate(info)
            if cls.is_valid_coordinate(x, y, width, height):
                return (x, y)
            else:
                raise ValueError()
        except ValueError:
            raise ValueError("Invalid ENTRY")

    @field_validator("exit", mode="before")
    @classmethod
    def exit_validate(cls, exit: str, info: ValidationInfo) -> tuple[int, int]:
        try:
            x, y = cls.assign_coordinate(exit)
            width, height, entry = cls.exit_info_validate(info)
            if cls.is_valid_coordinate(x, y, width, height) and (x, y) != entry:
                return (x, y)
            else:
                raise ValueError()
        except ValueError as e:
            raise ValueError("Invalid EXIT")


def convert_dict(entry_list: list[str]) -> dict[str, str]:
    entry_dict = {}
    for entry in entry_list:
        if entry == "\n":
            continue
        key, value = entry.split("=")
        if key in entry_dict.keys():
            raise KeyAlreadyExistError(key.upper())
        entry_dict.update({key: value})
    return entry_dict


def arg_parse() -> Config:

    parser = argparse.ArgumentParser()

    parser.add_argument("filename", type=open, help="設定ファイル")

    try:
        args = parser.parse_args()
        entry_list = [entry.strip().lower()
                      for entry in args.filename.readlines()
                      if entry[0] != "#" and entry[0] != " "
                      and entry[0] != "\n" and
                      entry.split("=")[0] == entry.split("=")[0].upper()]
        entry_dict = convert_dict(entry_list)
        config = Config(**entry_dict)
        return config
    except KeyAlreadyExistError as e:
        print(f"Error: Too many {e}")
        sys.exit(1)
    except ValidationError as e:
        error = e.errors()[0]
        if error["type"] == "missing":
            print(f"Error: Missing parameter: {error["loc"][0].upper()}")
            exit(1)
        print(e.errors()[0]["msg"])
        exit(1)
