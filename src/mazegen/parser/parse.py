from argparse import ArgumentParser
from random import randint
from sys import exit
from typing_extensions import Self
from typing import Optional, Union
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
    seed: Optional[int] = Field(default_factory=lambda: randint(0, 100))

    @classmethod
    def _to_int(cls, value: str) -> int:
        if "." in value:
            raise ParseError("Input should be a valid integer")
        return int(value)

    @field_validator('width', 'height', mode='before')
    @classmethod
    def parse_dimension(cls, value: str) -> int:
        result = cls._to_int(value)
        if result < 3:
            raise ParseError("Too small for generating mazes")
        return result

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


def _parse_config_lines(lines: list[str]) -> dict[str, str]:
    """
    設定ファイルの各行を読んでentry_dictに格納する
    """
    entry_dict: dict[str, str] = {}
    for entry in lines:
        if entry.startswith("#") or entry.startswith("\n"):
            continue
        try:
            key, value = entry.split("=")
        except ValueError as e:
            raise ParseError(
                f"Invalid line (expected KEY=VALUE): {entry.rstrip()}") from e
        if key not in CONFIG_OPTIONS:
            raise ParseError(f"Invalid Key: {key}")
        if key.lower() in entry_dict:
            raise ParseError(f"'{key}' already exits")
        entry_dict[key.lower()] = value.strip()
    return entry_dict


def _format_validation_error(e: ValidationError) -> str:
    """
    ValidationErrorを捕捉したときのエラーメッセージのフォーマット
    """
    err_msg = e.errors()[0]['msg'].replace("Value error, ", "")
    err_loc_val: Union[int, str] = ""
    err_loc = e.errors()[0]['loc']
    if len(err_loc):
        err_loc_val = err_loc[0]

        if err_loc_val != "seed":
            err_loc_val = str(err_loc_val).upper()
        return f"{err_msg}: {err_loc_val}"
    else:
        return err_msg


def arg_parse() -> Config:
    """
    argparseライブラリによる引数のパース
    """
    try:
        parser = ArgumentParser()
        parser.add_argument("filename", help="設定ファイル")
        args = parser.parse_args()
        with open(args.filename) as f:
            entry_dict = _parse_config_lines(f.readlines())
        return Config.model_validate(entry_dict)
    except ValidationError as e:
        print(_format_validation_error(e))
        exit(1)
    except (ParseError, OSError, ValueError) as e:
        print(e)
        exit(1)
