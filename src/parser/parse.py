from argparse import ArgumentParser
from random import randint
from sys import exit
from typing import Optional, Self, Any
from pydantic import BaseModel, field_validator, model_validator, \
    ValidationError, Field


ConfigOption = [
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE", "seed"
]


class Config(BaseModel):
    """
    迷路生成のための設定
    """
    width: int = Field(ge=0, le=100, strict=True)
    height: int = Field(ge=0, le=100, strict=True)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool = Field(default=False)
    seed: Optional[int] = Field(default=randint(0, 100))

    @field_validator('width', 'height', mode='before')
    @classmethod
    def parse_size(cls, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ValueError()

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def parse_coordinate(cls, value: str) -> tuple[int, int]:
        try:
            x, y = (int(p) for p in value.split(","))
            return (x, y)
        except ValueError:
            raise ValueError()

    @field_validator('perfect', mode="before")
    @classmethod
    def is_valid_perfect(cls, value: str) -> str:
        if value != "True" and value != "False":
            raise ValueError()
        return value

    @model_validator(mode="after")
    def is_valid_entry(self) -> Self:
        entry_x, entry_y = self.entry
        if (entry_x >= 0 and entry_x <= self.width - 1) and \
                (entry_y >= 0 and entry_y <= self.height - 1):
            return self
        raise ValueError()

    @model_validator(mode="after")
    def is_valid_exit(self) -> Self:
        exit_x, exit_y = self.exit
        if (exit_x >= 0 and exit_x <= self.width - 1) and \
            (exit_y >= 0 and exit_y <= self.height - 1) and \
                self.entry != self.exit:
            return self
        raise ValueError()


def arg_parse() -> Config:
    """
    argpauseライブラリによる引数のパース
    """
    try:
        parser = ArgumentParser()
        parser.add_argument("filename", type=open, help="設定ファイル")
        args = parser.parse_args()
        entry_dict: dict[str, Any] = {}

        for entry in args.filename.readlines():
            if entry.startswith("#"):
                continue
            elif entry.startswith(" ") and len(entry) > 0:
                raise ValueError()
            elif entry.startswith("\n"):
                continue
            key, value = entry.split("=")
            if key not in ConfigOption:
                raise ValueError()
            if key.lower() in entry_dict.keys():
                raise ValueError()
            entry_dict[key.lower()] = value.strip()
        config = Config(**entry_dict)
        return config
    except (ValidationError, ValueError):
        print("Invalid Input")
        exit(1)
    except FileNotFoundError as e:
        print(e)
        exit(1)
