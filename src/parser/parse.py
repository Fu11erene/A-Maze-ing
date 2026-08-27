import argparse
from sys import exit
from typing import Optional, Self, Any
from random import randint
from enum import Enum, auto
from pydantic import BaseModel, field_validator, model_validator, ValidationError, Field
from pydantic_core.core_schema import ValidationInfo


ConfigOption = [
    "WIDTH", "HEIGHT", "ENTRY", "PERFECT", "OUTPUT_FILE ", "seed"
]


class Config(BaseModel):
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool = Field(default=False)
    seed: Optional[int] = Field(default=randint(0, 100))

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def parse_coordinate(cls, value: Any) -> tuple[Any, Any]:
        try:
            x, y = (int(p) for p in value.split(","))
            return (x, y)
        except ValueError:
            raise ValueError(f"Invalid coordinate: {value}")

    @model_validator(mode="after")
    def is_valid_entry(self) -> Self:
        entry_x, entry_y = self.entry
        if (entry_x >= 0 and entry_x <= self.width - 1) and (entry_y >= 0 and entry_y <= self.height - 1):
            return self
        raise ValueError()

    @model_validator(mode="after")
    def is_valid_exit(self) -> Self:
        exit_x, exit_y = self.exit
        if (exit_x >= 0 and exit_x <= self.width - 1) and (exit_y >= 0 and exit_y <= self.height - 1) and self.entry != self.exit:
            return self
        raise ValueError()


def arg_parse() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=open, help="設定ファイル")

    try:
        args = parser.parse_args()
        entry_dict = {}
        for entry in args.filename.readlines():
            if entry.startswith("#"):
                continue
            if entry.startswith(" "):
                continue
            if entry.startswith("\n"):
                continue
            key, value = entry.split("=")
            if key not in ConfigOption:
                ValueError("Invalid Key")
            entry_dict[key.lower()] = value.strip()
        config = Config(**entry_dict)
        return config
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except ValidationError as e:
        print(e)
        exit(1)
