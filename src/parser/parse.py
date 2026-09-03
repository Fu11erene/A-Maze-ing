from argparse import ArgumentParser
from random import randint
from typing import Optional, Self, Any
from pydantic import BaseModel, field_validator, model_validator, Field, ValidationError
from ..types import Coordinate
from ..errors import ParseError


CONFIG_OPTIONS = [
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE", "seed"
]


class Config(BaseModel):
    """
    迷路生成のための設定
    """
    width: int = Field(ge=0, le=100, strict=True)
    height: int = Field(ge=0, le=100, strict=True)
    entry: Coordinate
    exit: Coordinate
    output_file: str
    perfect: bool = Field(default=False)
    seed: Optional[int] = Field(default=randint(0, 100))

    @field_validator('width', mode='before')
    @classmethod
    def parse_width(cls, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ParseError("Invalid 'WIDTH'")

    @field_validator('height', mode='before')
    @classmethod
    def parse_hight(cls, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ParseError("Invalid 'HIGHT'")

    @field_validator('entry', mode='before')
    @classmethod
    def parse_entry(cls, value: str) -> Coordinate:
        try:
            x, y = (int(p) for p in value.split(","))
            return (x, y)
        except ValueError:
            raise ParseError("Invalid 'ENTRY'")

    @field_validator('exit', mode='before')
    @classmethod
    def parse_exit(cls, value: str) -> Coordinate:
        try:
            x, y = (int(p) for p in value.split(","))
            return (x, y)
        except ValueError:
            raise ParseError("Invalid 'EXIT'")

    @field_validator('perfect', mode="before")
    @classmethod
    def is_valid_perfect(cls, value: str) -> str:
        if value != "True" and value != "False":
            raise ParseError("Invalid 'perfect'")
        return value

    @model_validator(mode="after")
    def is_valid_entry(self) -> Self:
        entry_x, entry_y = self.entry
        if (entry_x >= 0 and entry_x <= self.width - 1) and \
                (entry_y >= 0 and entry_y <= self.height - 1):
            return self
        raise ParseError("Invalid 'ENTRY'")

    @model_validator(mode="after")
    def is_valid_exit(self) -> Self:
        exit_x, exit_y = self.exit
        if (exit_x >= 0 and exit_x <= self.width - 1) and \
            (exit_y >= 0 and exit_y <= self.height - 1) and \
                self.entry != self.exit:
            return self
        raise ParseError("Invalid 'EXIT'")


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
            key, value = entry.split("=")
            if key not in CONFIG_OPTIONS:
                raise ParseError("Invalid Key")
            if key.lower() in entry_dict.keys():
                raise ParseError(f"'{key}' already exits")
            entry_dict[key.lower()] = value.strip()
        config = Config(**entry_dict)
        return config
    except (ParseError, FileNotFoundError, PermissionError) as e:
        raise ParseError(e)
