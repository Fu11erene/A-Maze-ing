import re
from argparse import ArgumentParser
from random import randint
from sys import exit
from typing import Optional, Self, Any
from pydantic import BaseModel, field_validator, model_validator, \
    Field, ValidationError
from ..types import Coordinate
from ..errors import ParseError


CONFIG_OPTIONS = [
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE", "seed"
]


class Config(BaseModel):
    """
    迷路生成のための設定
    """
    width: int = Field(ge=0, le=100)
    height: int = Field(ge=0, le=100)
    entry: Coordinate
    exit: Coordinate
    output_file: str
    perfect: bool = Field(default=False)
    seed: Optional[int] = Field(default=randint(0, 100))

    @classmethod
    def _to_int(cls, value: str) -> int:
        if "." in value:
            raise ValueError("Input should be a valid integer")
        return int(value)

    @field_validator('width', 'height', mode='before')
    @classmethod
    def parse_dimension(cls, value: str) -> int:
        return cls._to_int(value)

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def parse_entry(cls, value: str) -> Coordinate:
        x, y = value.split(",")
        return (cls._to_int(x), cls._to_int(y))

    @field_validator('perfect', mode="before")
    @classmethod
    def is_valid_perfect(cls, value: str) -> bool:
        if value == "True":
            return True
        if value == "False":
            return False
        raise ParseError(
            "'perfect' should be 'True' or 'False'")

    def _in_bounds(self, point: Coordinate) -> bool:
        x, y = point
        return 0 <= x <= self.width - 1 and 0 <= y <= self.height - 1

    @model_validator(mode="after")
    def validate_entry_and_exit(self) -> Self:
        if not self._in_bounds(self.entry):
            raise ParseError("Invalid 'ENTRY'")
        if not self._in_bounds(self.exit):
            raise ParseError("Invalid 'EXIT'")
        if self.entry == self.exit:
            raise ParseError("Invalid 'EXIT'")
        return self


def arg_parse() -> Config:
    """
    argparseライブラリによる引数のパース
    """
    try:
        parser = ArgumentParser()
        parser.add_argument("filename", type=open, help="設定ファイル")
        args = parser.parse_args()
        entry_dict: dict[str, Any] = {}

        for entry in args.filename.readlines():
            if entry.startswith("#"):
                continue
            elif entry.startswith("\n"):
                continue
            try:
                key, value = entry.split("=")
            except ValueError as e:
                raise ParseError(
                    "Invalid line"
                    f"(expected KEY=VALUE): {entry.rstrip()}") from e
            if key not in CONFIG_OPTIONS:
                raise ParseError(f"Invalid Key: {key}")
            if key.lower() in entry_dict.keys():
                raise ParseError(f"'{key}' already exits")
            entry_dict[key.lower()] = value.strip()
        config = Config(**entry_dict)
        return config
    except ValidationError as e:
        err_loc = e.errors()[0]['loc'][0]
        err_msg = e.errors()[0]['msg'].replace("Value error, ", "")

        if err_loc != "seed":
            err_loc = str(err_loc).upper()
        print(f"{err_msg}: {err_loc}")
        exit(1)
    except (ParseError, FileNotFoundError, PermissionError) as e:
        print(e)
        exit(1)
