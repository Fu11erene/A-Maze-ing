"""Tests covering the valid-input equivalence classes for
src.parser.parse.arg_parse.

tests/test_parse_invalid.py exhaustively checks that malformed input is
rejected, but never checks that a well-formed config file is actually
*accepted* and parsed into the expected values. This file closes that gap:
it exercises the valid equivalence class for every field, the valid side of
each boundary (as opposed to the invalid side already covered), and the
"all conditions true" row of the is_valid_entry / is_valid_exit decision
tables.
"""

import sys
from pathlib import Path
from typing import Optional

import pytest

from src.parser.parse import Config, arg_parse


def build_config_text(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    output_file: str = "maze.txt",
    perfect: Optional[str] = "True",
    seed: Optional[str] = None,
) -> str:
    lines = [
        f"WIDTH={width}",
        f"HEIGHT={height}",
        f"ENTRY={entry[0]},{entry[1]}",
        f"EXIT={exit_[0]},{exit_[1]}",
        f"OUTPUT_FILE={output_file}",
    ]
    if perfect is not None:
        lines.append(f"PERFECT={perfect}")
    if seed is not None:
        lines.append(f"seed={seed}")
    return "\n".join(lines) + "\n"


def run_arg_parse_valid(tmp_path: Path, content: str) -> Config:
    config_file = tmp_path / "config.txt"
    config_file.write_text(content)
    sys.argv = ["a_maze_ing.py", str(config_file)]
    return arg_parse()


def test_baseline_valid_config_succeeds(tmp_path: Path) -> None:
    content = build_config_text(20, 15, (0, 0), (19, 14), "maze.txt", "True")
    config = run_arg_parse_valid(tmp_path, content)
    assert config.width == 20
    assert config.height == 15
    assert config.entry == (0, 0)
    assert config.exit == (19, 14)
    assert config.output_file == "maze.txt"
    assert config.perfect is True


def test_perfect_false_is_accepted(tmp_path: Path) -> None:
    content = build_config_text(20, 15, (0, 0), (19, 14), perfect="False")
    config = run_arg_parse_valid(tmp_path, content)
    assert config.perfect is False


def test_width_upper_boundary_100_is_accepted(tmp_path: Path) -> None:
    # width=100 is the exact ge=0/le=100 upper boundary, and entry/exit's
    # x=99 (=width-1) is the exact upper boundary of the coordinate check.
    content = build_config_text(100, 15, (0, 0), (99, 14))
    config = run_arg_parse_valid(tmp_path, content)
    assert config.width == 100
    assert config.exit == (99, 14)


def test_height_upper_boundary_100_is_accepted(tmp_path: Path) -> None:
    content = build_config_text(15, 100, (0, 0), (14, 99))
    config = run_arg_parse_valid(tmp_path, content)
    assert config.height == 100
    assert config.exit == (14, 99)


def test_width_lower_boundary_1_is_accepted(tmp_path: Path) -> None:
    # width=1 is the smallest width that can still hold two distinct cells
    # (paired with height=2). width=0 can never succeed (see
    # test_parse_invalid.py::width_zero_leaves_no_room_for_entry) so it is
    # not a valid boundary value despite passing width's own ge=0 check.
    content = build_config_text(1, 2, (0, 0), (0, 1))
    config = run_arg_parse_valid(tmp_path, content)
    assert config.width == 1
    assert config.entry == (0, 0)
    assert config.exit == (0, 1)


def test_height_lower_boundary_1_is_accepted(tmp_path: Path) -> None:
    content = build_config_text(2, 1, (0, 0), (1, 0))
    config = run_arg_parse_valid(tmp_path, content)
    assert config.height == 1
    assert config.entry == (0, 0)
    assert config.exit == (1, 0)


def test_entry_at_far_corner_is_accepted(tmp_path: Path) -> None:
    # Covers the "all conditions true" row of is_valid_entry with entry
    # itself sitting on the upper boundary (previous boundary tests only
    # ever exercised exit at the far corner).
    content = build_config_text(20, 15, (19, 14), (0, 0))
    config = run_arg_parse_valid(tmp_path, content)
    assert config.entry == (19, 14)
    assert config.exit == (0, 0)


def test_seed_provided_is_used(tmp_path: Path) -> None:
    content = build_config_text(20, 15, (0, 0), (19, 14), seed="42")
    config = run_arg_parse_valid(tmp_path, content)
    assert config.seed == 42


def test_seed_omitted_falls_back_to_default(tmp_path: Path) -> None:
    content = build_config_text(20, 15, (0, 0), (19, 14), seed=None)
    config = run_arg_parse_valid(tmp_path, content)
    assert isinstance(config.seed, int)


OUTPUT_FILE_VALID_VALUES = [
    ("simple_filename", "maze.txt"),
    ("empty_string", ""),
    ("path_with_directories", "output/maze.txt"),
    ("unicode_filename", "迷路.txt"),
    ("filename_with_spaces", "my maze.txt"),
    ("filename_with_emoji", "💀.txt"),
    ("long_filename", "a" * 200 + ".txt"),
    ("dot_only", "."),
    ("no_extension", "maze"),
]


@pytest.mark.parametrize(
    "value", [v for _, v in OUTPUT_FILE_VALID_VALUES],
    ids=[name for name, _ in OUTPUT_FILE_VALID_VALUES],
)
def test_output_file_accepts_any_string(tmp_path: Path, value: str) -> None:
    content = build_config_text(20, 15, (0, 0), (19, 14), output_file=value)
    config = run_arg_parse_valid(tmp_path, content)
    assert config.output_file == value
