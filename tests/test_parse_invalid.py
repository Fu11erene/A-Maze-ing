"""Tests covering invalid config inputs for mazegen.parser.parse.arg_parse.

The parser must reject any malformed / out-of-spec configuration file and
exit with status code 1 while printing a clear error message, instead of
crashing or silently accepting bad data (see subject IV.2: "Your program
must handle all errors gracefully ... It must never crash unexpectedly").
"""

import sys
from pathlib import Path
from typing import Optional, Any

import pytest

from mazegen.parser.parse import arg_parse


# A known-valid baseline config. Each test case starts from this and
# mutates exactly one aspect to make it invalid.
VALID_LINES = {
    "WIDTH": "WIDTH=20",
    "HEIGHT": "HEIGHT=15",
    "ENTRY": "ENTRY=0,0",
    "EXIT": "EXIT=19,14",
    "OUTPUT_FILE": "OUTPUT_FILE=maze.txt",
    "PERFECT": "PERFECT=True",
}


def build_config(**overrides: Optional[str]) -> str:
    """Build config text from the valid baseline, applying overrides.

    Passing None for a key removes that line entirely (simulating a
    missing mandatory key). Otherwise the value replaces that key's line.
    """
    lines = dict(VALID_LINES)
    for key, value in overrides.items():
        if value is None:
            lines.pop(key, None)
        else:
            lines[key] = value
    return "\n".join(lines.values()) + "\n"


def run_arg_parse(tmp_path: Path, content: str) -> pytest.ExceptionInfo[SystemExit]:
    config_file = tmp_path / "config.txt"
    config_file.write_text(content)
    sys.argv = ["a_maze_ing.py", str(config_file)]
    with pytest.raises(SystemExit) as exc_info:
        arg_parse()
    return exc_info


INVALID_CASES: list[tuple[str, dict[str, Optional[str]]]] = [
    # --- Missing mandatory keys ---
    ("missing_width", dict(WIDTH=None)),
    ("missing_height", dict(HEIGHT=None)),
    ("missing_entry", dict(ENTRY=None)),
    ("missing_exit", dict(EXIT=None)),
    ("missing_output_file", dict(OUTPUT_FILE=None)),

    # --- WIDTH invalid values ---
    ("width_non_integer", dict(WIDTH="WIDTH=abc")),
    ("width_negative", dict(WIDTH="WIDTH=-1")),
    ("width_too_small", dict(WIDTH="WIDTH=2")),
    ("width_too_large", dict(WIDTH="WIDTH=101")),
    ("width_float", dict(WIDTH="WIDTH=20.5")),
    ("width_empty_value", dict(WIDTH="WIDTH=")),
    ("width_missing_value_no_equals", dict(WIDTH="WIDTH")),
    ("width_hex_value", dict(WIDTH="WIDTH=0x14")),
    ("width_leading_zero_garbage", dict(WIDTH="WIDTH=20abc")),

    # --- WIDTH type-related edge cases ---
    ("width_scientific_notation", dict(WIDTH="WIDTH=2e1")),
    ("width_negative_float", dict(WIDTH="WIDTH=-1.5")),
    ("width_positive_float_with_plus", dict(WIDTH="WIDTH=+20.5")),
    ("width_double_negative_sign", dict(WIDTH="WIDTH=--20")),
    ("width_trailing_minus", dict(WIDTH="WIDTH=20-")),
    ("width_trailing_plus", dict(WIDTH="WIDTH=20+")),
    ("width_internal_space", dict(WIDTH="WIDTH=2 0")),
    ("width_internal_tab", dict(WIDTH="WIDTH=20\t5")),
    ("width_comma_thousands_separator", dict(WIDTH="WIDTH=1,000")),
    ("width_underscore_separator_over_limit", dict(WIDTH="WIDTH=1_000")),
    ("width_binary_literal_string", dict(WIDTH="WIDTH=0b10100")),
    ("width_octal_literal_string", dict(WIDTH="WIDTH=0o24")),
    ("width_long_suffix", dict(WIDTH="WIDTH=20L")),
    ("width_boolean_word_true", dict(WIDTH="WIDTH=True")),
    ("width_boolean_word_false", dict(WIDTH="WIDTH=False")),
    ("width_none_word", dict(WIDTH="WIDTH=None")),
    ("width_null_word", dict(WIDTH="WIDTH=null")),
    ("width_nan_word", dict(WIDTH="WIDTH=NaN")),
    ("width_infinity_word", dict(WIDTH="WIDTH=Infinity")),
    ("width_negative_infinity", dict(WIDTH="WIDTH=-inf")),
    ("width_arithmetic_expression_div", dict(WIDTH="WIDTH=20/2")),
    ("width_arithmetic_expression_mul", dict(WIDTH="WIDTH=20*1")),
    ("width_huge_number", dict(WIDTH="WIDTH=999999999999999999999999")),
    ("width_very_negative_number", dict(WIDTH="WIDTH=-999999999999999999999999")),
    ("width_negative_zero", dict(WIDTH="WIDTH=-0")),

    # --- HEIGHT invalid values ---
    ("height_non_integer", dict(HEIGHT="HEIGHT=xyz")),
    ("height_negative", dict(HEIGHT="HEIGHT=-5")),
    ("height_too_small", dict(HEIGHT="HEIGHT=2")),
    ("height_too_large", dict(HEIGHT="HEIGHT=999")),
    ("height_too_large_101", dict(HEIGHT="HEIGHT=101")),
    ("height_float", dict(HEIGHT="HEIGHT=15.0")),
    ("height_empty_value", dict(HEIGHT="HEIGHT=")),
    ("height_missing_value_no_equals", dict(HEIGHT="HEIGHT")),
    ("height_hex_value", dict(HEIGHT="HEIGHT=0xF")),

    # --- HEIGHT type-related edge cases ---
    ("height_scientific_notation", dict(HEIGHT="HEIGHT=2e1")),
    ("height_negative_float", dict(HEIGHT="HEIGHT=-1.5")),
    ("height_positive_float_with_plus", dict(HEIGHT="HEIGHT=+20.5")),
    ("height_double_negative_sign", dict(HEIGHT="HEIGHT=--20")),
    ("height_trailing_minus", dict(HEIGHT="HEIGHT=20-")),
    ("height_trailing_plus", dict(HEIGHT="HEIGHT=20+")),
    ("height_internal_space", dict(HEIGHT="HEIGHT=2 0")),
    ("height_internal_tab", dict(HEIGHT="HEIGHT=20\t5")),
    ("height_comma_thousands_separator", dict(HEIGHT="HEIGHT=1,000")),
    ("height_underscore_separator_over_limit", dict(HEIGHT="HEIGHT=1_000")),
    ("height_binary_literal_string", dict(HEIGHT="HEIGHT=0b10100")),
    ("height_octal_literal_string", dict(HEIGHT="HEIGHT=0o24")),
    ("height_long_suffix", dict(HEIGHT="HEIGHT=20L")),
    ("height_boolean_word_true", dict(HEIGHT="HEIGHT=True")),
    ("height_boolean_word_false", dict(HEIGHT="HEIGHT=False")),
    ("height_none_word", dict(HEIGHT="HEIGHT=None")),
    ("height_null_word", dict(HEIGHT="HEIGHT=null")),
    ("height_nan_word", dict(HEIGHT="HEIGHT=NaN")),
    ("height_infinity_word", dict(HEIGHT="HEIGHT=Infinity")),
    ("height_negative_infinity", dict(HEIGHT="HEIGHT=-inf")),
    ("height_arithmetic_expression_div", dict(HEIGHT="HEIGHT=20/2")),
    ("height_arithmetic_expression_mul", dict(HEIGHT="HEIGHT=20*1")),
    ("height_huge_number", dict(HEIGHT="HEIGHT=999999999999999999999999")),
    ("height_very_negative_number", dict(HEIGHT="HEIGHT=-999999999999999999999999")),
    ("height_negative_zero", dict(HEIGHT="HEIGHT=-0")),

    # --- ENTRY invalid values ---
    ("entry_missing_comma", dict(ENTRY="ENTRY=00")),
    ("entry_non_integer", dict(ENTRY="ENTRY=a,b")),
    ("entry_single_value", dict(ENTRY="ENTRY=0")),
    ("entry_three_values", dict(ENTRY="ENTRY=0,0,0")),
    ("entry_out_of_bounds_x", dict(ENTRY="ENTRY=20,0")),
    ("entry_out_of_bounds_y", dict(ENTRY="ENTRY=0,15")),
    ("entry_negative_x", dict(ENTRY="ENTRY=-1,0")),
    ("entry_negative_y", dict(ENTRY="ENTRY=0,-1")),
    ("entry_float_coordinates", dict(ENTRY="ENTRY=0.0,0")),
    ("entry_float_y_coordinate", dict(ENTRY="ENTRY=0,0.0")),
    ("entry_float_both_coordinates", dict(ENTRY="ENTRY=0.0,1.0")),
    ("entry_negative_float_coordinate", dict(ENTRY="ENTRY=-0.5,0")),
    ("entry_scientific_notation", dict(ENTRY="ENTRY=1e1,0")),
    ("entry_empty_value", dict(ENTRY="ENTRY=")),
    ("entry_trailing_comma", dict(ENTRY="ENTRY=0,")),
    ("entry_equal_to_exit", dict(ENTRY="ENTRY=19,14")),

    # --- ENTRY type-related edge cases (x coordinate) ---
    ("entry_x_scientific_notation_alt", dict(ENTRY="ENTRY=2e1,5")),
    ("entry_x_positive_float_with_plus", dict(ENTRY="ENTRY=+5.5,5")),
    ("entry_x_double_negative_sign", dict(ENTRY="ENTRY=--3,5")),
    ("entry_x_trailing_minus", dict(ENTRY="ENTRY=3-,5")),
    ("entry_x_trailing_plus", dict(ENTRY="ENTRY=3+,5")),
    ("entry_x_internal_space", dict(ENTRY="ENTRY=3 3,5")),
    ("entry_x_internal_tab", dict(ENTRY="ENTRY=3\t3,5")),
    ("entry_x_underscore_separator_over_limit", dict(ENTRY="ENTRY=1_000,5")),
    ("entry_x_binary_literal_string", dict(ENTRY="ENTRY=0b101,5")),
    ("entry_x_octal_literal_string", dict(ENTRY="ENTRY=0o17,5")),
    ("entry_x_long_suffix", dict(ENTRY="ENTRY=5L,5")),
    ("entry_x_boolean_word_true", dict(ENTRY="ENTRY=True,5")),
    ("entry_x_boolean_word_false", dict(ENTRY="ENTRY=False,5")),
    ("entry_x_none_word", dict(ENTRY="ENTRY=None,5")),
    ("entry_x_null_word", dict(ENTRY="ENTRY=null,5")),
    ("entry_x_nan_word", dict(ENTRY="ENTRY=NaN,5")),
    ("entry_x_infinity_word", dict(ENTRY="ENTRY=Infinity,5")),
    ("entry_x_negative_infinity", dict(ENTRY="ENTRY=-inf,5")),
    ("entry_x_arithmetic_expression_div", dict(ENTRY="ENTRY=6/2,5")),
    ("entry_x_arithmetic_expression_mul", dict(ENTRY="ENTRY=6*1,5")),
    ("entry_x_huge_number", dict(ENTRY="ENTRY=999999999999999999999999,5")),
    ("entry_x_very_negative_number", dict(ENTRY="ENTRY=-999999999999999999999999,5")),
    ("entry_x_multi_digit_float", dict(ENTRY="ENTRY=12.34,5")),
    ("entry_x_double_dot_float", dict(ENTRY="ENTRY=3..3,5")),
    ("entry_x_hex_value", dict(ENTRY="ENTRY=0x14,5")),

    # --- ENTRY type-related edge cases (y coordinate) ---
    ("entry_y_scientific_notation_alt", dict(ENTRY="ENTRY=5,2e1")),
    ("entry_y_positive_float_with_plus", dict(ENTRY="ENTRY=5,+5.5")),
    ("entry_y_double_negative_sign", dict(ENTRY="ENTRY=5,--3")),
    ("entry_y_trailing_minus", dict(ENTRY="ENTRY=5,3-")),
    ("entry_y_trailing_plus", dict(ENTRY="ENTRY=5,3+")),
    ("entry_y_internal_space", dict(ENTRY="ENTRY=5,3 3")),
    ("entry_y_internal_tab", dict(ENTRY="ENTRY=5,3\t3")),
    ("entry_y_underscore_separator_over_limit", dict(ENTRY="ENTRY=5,1_000")),
    ("entry_y_binary_literal_string", dict(ENTRY="ENTRY=5,0b101")),
    ("entry_y_octal_literal_string", dict(ENTRY="ENTRY=5,0o17")),
    ("entry_y_long_suffix", dict(ENTRY="ENTRY=5,5L")),
    ("entry_y_boolean_word_true", dict(ENTRY="ENTRY=5,True")),
    ("entry_y_boolean_word_false", dict(ENTRY="ENTRY=5,False")),
    ("entry_y_none_word", dict(ENTRY="ENTRY=5,None")),
    ("entry_y_null_word", dict(ENTRY="ENTRY=5,null")),
    ("entry_y_nan_word", dict(ENTRY="ENTRY=5,NaN")),
    ("entry_y_infinity_word", dict(ENTRY="ENTRY=5,Infinity")),
    ("entry_y_negative_infinity", dict(ENTRY="ENTRY=5,-inf")),
    ("entry_y_arithmetic_expression_div", dict(ENTRY="ENTRY=5,6/2")),
    ("entry_y_arithmetic_expression_mul", dict(ENTRY="ENTRY=5,6*1")),
    ("entry_y_huge_number", dict(ENTRY="ENTRY=5,999999999999999999999999")),
    ("entry_y_very_negative_number", dict(ENTRY="ENTRY=5,-999999999999999999999999")),
    ("entry_y_multi_digit_float", dict(ENTRY="ENTRY=5,12.34")),
    ("entry_y_double_dot_float", dict(ENTRY="ENTRY=5,3..3")),
    ("entry_y_hex_value", dict(ENTRY="ENTRY=5,0x14")),

    # --- EXIT invalid values ---
    ("exit_missing_comma", dict(EXIT="EXIT=1914")),
    ("exit_non_integer", dict(EXIT="EXIT=a,b")),
    ("exit_single_value", dict(EXIT="EXIT=19")),
    ("exit_out_of_bounds_x", dict(EXIT="EXIT=20,14")),
    ("exit_out_of_bounds_y", dict(EXIT="EXIT=19,15")),
    ("exit_negative_x", dict(EXIT="EXIT=-1,14")),
    ("exit_negative_y", dict(EXIT="EXIT=19,-1")),
    ("exit_equal_to_entry", dict(EXIT="EXIT=0,0")),
    ("exit_empty_value", dict(EXIT="EXIT=")),
    ("exit_float_coordinates", dict(EXIT="EXIT=19.0,14")),
    ("exit_float_y_coordinate", dict(EXIT="EXIT=19,14.0")),
    ("exit_float_both_coordinates", dict(EXIT="EXIT=19.0,14.0")),
    ("exit_negative_float_coordinate", dict(EXIT="EXIT=-1.0,14")),
    ("exit_scientific_notation", dict(EXIT="EXIT=1e1,14")),

    # --- EXIT type-related edge cases (x coordinate) ---
    ("exit_x_scientific_notation_alt", dict(EXIT="EXIT=2e1,5")),
    ("exit_x_positive_float_with_plus", dict(EXIT="EXIT=+5.5,5")),
    ("exit_x_double_negative_sign", dict(EXIT="EXIT=--3,5")),
    ("exit_x_trailing_minus", dict(EXIT="EXIT=3-,5")),
    ("exit_x_trailing_plus", dict(EXIT="EXIT=3+,5")),
    ("exit_x_internal_space", dict(EXIT="EXIT=3 3,5")),
    ("exit_x_internal_tab", dict(EXIT="EXIT=3\t3,5")),
    ("exit_x_underscore_separator_over_limit", dict(EXIT="EXIT=1_000,5")),
    ("exit_x_binary_literal_string", dict(EXIT="EXIT=0b101,5")),
    ("exit_x_octal_literal_string", dict(EXIT="EXIT=0o17,5")),
    ("exit_x_long_suffix", dict(EXIT="EXIT=5L,5")),
    ("exit_x_boolean_word_true", dict(EXIT="EXIT=True,5")),
    ("exit_x_boolean_word_false", dict(EXIT="EXIT=False,5")),
    ("exit_x_none_word", dict(EXIT="EXIT=None,5")),
    ("exit_x_null_word", dict(EXIT="EXIT=null,5")),
    ("exit_x_nan_word", dict(EXIT="EXIT=NaN,5")),
    ("exit_x_infinity_word", dict(EXIT="EXIT=Infinity,5")),
    ("exit_x_negative_infinity", dict(EXIT="EXIT=-inf,5")),
    ("exit_x_arithmetic_expression_div", dict(EXIT="EXIT=6/2,5")),
    ("exit_x_arithmetic_expression_mul", dict(EXIT="EXIT=6*1,5")),
    ("exit_x_huge_number", dict(EXIT="EXIT=999999999999999999999999,5")),
    ("exit_x_very_negative_number", dict(EXIT="EXIT=-999999999999999999999999,5")),
    ("exit_x_multi_digit_float", dict(EXIT="EXIT=12.34,5")),
    ("exit_x_double_dot_float", dict(EXIT="EXIT=3..3,5")),
    ("exit_x_hex_value", dict(EXIT="EXIT=0x14,5")),

    # --- EXIT type-related edge cases (y coordinate) ---
    ("exit_y_scientific_notation_alt", dict(EXIT="EXIT=5,2e1")),
    ("exit_y_positive_float_with_plus", dict(EXIT="EXIT=5,+5.5")),
    ("exit_y_double_negative_sign", dict(EXIT="EXIT=5,--3")),
    ("exit_y_trailing_minus", dict(EXIT="EXIT=5,3-")),
    ("exit_y_trailing_plus", dict(EXIT="EXIT=5,3+")),
    ("exit_y_internal_space", dict(EXIT="EXIT=5,3 3")),
    ("exit_y_internal_tab", dict(EXIT="EXIT=5,3\t3")),
    ("exit_y_underscore_separator_over_limit", dict(EXIT="EXIT=5,1_000")),
    ("exit_y_binary_literal_string", dict(EXIT="EXIT=5,0b101")),
    ("exit_y_octal_literal_string", dict(EXIT="EXIT=5,0o17")),
    ("exit_y_long_suffix", dict(EXIT="EXIT=5,5L")),
    ("exit_y_boolean_word_true", dict(EXIT="EXIT=5,True")),
    ("exit_y_boolean_word_false", dict(EXIT="EXIT=5,False")),
    ("exit_y_none_word", dict(EXIT="EXIT=5,None")),
    ("exit_y_null_word", dict(EXIT="EXIT=5,null")),
    ("exit_y_nan_word", dict(EXIT="EXIT=5,NaN")),
    ("exit_y_infinity_word", dict(EXIT="EXIT=5,Infinity")),
    ("exit_y_negative_infinity", dict(EXIT="EXIT=5,-inf")),
    ("exit_y_arithmetic_expression_div", dict(EXIT="EXIT=5,6/2")),
    ("exit_y_arithmetic_expression_mul", dict(EXIT="EXIT=5,6*1")),
    ("exit_y_huge_number", dict(EXIT="EXIT=5,999999999999999999999999")),
    ("exit_y_very_negative_number", dict(EXIT="EXIT=5,-999999999999999999999999")),
    ("exit_y_multi_digit_float", dict(EXIT="EXIT=5,12.34")),
    ("exit_y_double_dot_float", dict(EXIT="EXIT=5,3..3")),
    ("exit_y_hex_value", dict(EXIT="EXIT=5,0x14")),

    # --- OUTPUT_FILE structural edge cases ---
    # output_file is a plain `str` with no value-level validation, so any
    # string content is accepted. The only way an OUTPUT_FILE line can make
    # the config invalid is through how the line itself is structured
    # (key spelling/casing, equals-sign placement, duplication).
    ("output_file_lowercase_key", dict(OUTPUT_FILE="output_file=maze.txt")),
    ("output_file_titlecase_key", dict(OUTPUT_FILE="Output_File=maze.txt")),
    ("output_file_mixed_case_key", dict(OUTPUT_FILE="Output_file=maze.txt")),
    ("output_file_alternating_case_key", dict(OUTPUT_FILE="OuTpUt_FiLe=maze.txt")),
    ("output_file_hyphen_key", dict(OUTPUT_FILE="OUTPUT-FILE=maze.txt")),
    ("output_file_lowercase_hyphen_key", dict(OUTPUT_FILE="output-file=maze.txt")),
    ("output_file_no_underscore_key", dict(OUTPUT_FILE="OUTPUTFILE=maze.txt")),
    ("output_file_double_underscore_key", dict(OUTPUT_FILE="OUTPUT__FILE=maze.txt")),
    ("output_file_trailing_underscore_key", dict(OUTPUT_FILE="OUTPUT_FILE_=maze.txt")),
    ("output_file_leading_underscore_key", dict(OUTPUT_FILE="_OUTPUT_FILE=maze.txt")),
    ("output_file_digit_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE1=maze.txt")),
    ("output_file_digit_substitution_key", dict(OUTPUT_FILE="OUTPUT_F1LE=maze.txt")),
    ("output_file_missing_letter_key", dict(OUTPUT_FILE="OUTPUTFIL=maze.txt")),
    ("output_file_extra_letter_key", dict(OUTPUT_FILE="OUTPUT_FILEE=maze.txt")),
    ("output_file_space_before_equals_key", dict(OUTPUT_FILE="OUTPUT_FILE =maze.txt")),
    ("output_file_tab_before_equals_key", dict(OUTPUT_FILE="OUTPUT_FILE\t=maze.txt")),
    ("output_file_dot_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE.=maze.txt")),
    ("output_file_space_inside_key", dict(OUTPUT_FILE="OUTPUT FILE=maze.txt")),
    ("output_file_exclamation_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE!=maze.txt")),
    ("output_file_question_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE?=maze.txt")),
    ("output_file_asterisk_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE*=maze.txt")),
    ("output_file_hash_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE#=maze.txt")),
    ("output_file_leading_tab_line", dict(OUTPUT_FILE="\tOUTPUT_FILE=maze.txt")),
    ("output_file_colon_instead_of_equals", dict(OUTPUT_FILE="OUTPUT_FILE:maze.txt")),
    ("output_file_fullwidth_key", dict(OUTPUT_FILE="ＯＵＴＰＵＴ_ＦＩＬＥ=maze.txt")),
    ("output_file_extra_equals_one", dict(OUTPUT_FILE="OUTPUT_FILE=a=b")),
    ("output_file_extra_equals_two", dict(OUTPUT_FILE="OUTPUT_FILE=a=b=c")),
    ("output_file_extra_equals_three", dict(OUTPUT_FILE="OUTPUT_FILE=a=b=c=d")),
    ("output_file_extra_equals_four", dict(OUTPUT_FILE="OUTPUT_FILE=a=b=c=d=e")),
    ("output_file_many_equals", dict(OUTPUT_FILE="OUTPUT_FILE=a=b=c=d=e=f=g")),
    ("output_file_double_equals", dict(OUTPUT_FILE="OUTPUT_FILE==maze.txt")),
    ("output_file_trailing_equals", dict(OUTPUT_FILE="OUTPUT_FILE=maze.txt=")),
    ("output_file_triple_bare_equals", dict(OUTPUT_FILE="OUTPUT_FILE====")),
    ("output_file_equals_in_filename", dict(OUTPUT_FILE="OUTPUT_FILE=maze=.txt")),
    ("output_file_duplicate_value_halves", dict(OUTPUT_FILE="OUTPUT_FILE=maze.txt=maze.txt")),
    ("output_file_leading_equals", dict(OUTPUT_FILE="=OUTPUT_FILE=maze.txt")),
    ("output_file_equals_in_middle_twice", dict(OUTPUT_FILE="OUTPUT_FILE=x==y")),
    ("output_file_multiple_equals_with_spaces", dict(OUTPUT_FILE="OUTPUT_FILE= = ")),
    ("output_file_missing_value_no_equals", dict(OUTPUT_FILE="OUTPUT_FILE")),
    ("output_file_no_equals_typo_key", dict(OUTPUT_FILE="OUTPUTFILE")),
    ("output_file_lowercase_no_equals", dict(OUTPUT_FILE="output_file")),
    ("output_file_space_instead_of_equals", dict(OUTPUT_FILE="OUTPUT_FILE maze.txt")),
    ("duplicate_output_file_key", dict(OUTPUT_FILE="OUTPUT_FILE=maze.txt\nOUTPUT_FILE=other.txt")),
    ("duplicate_output_file_key_same_value", dict(OUTPUT_FILE="OUTPUT_FILE=maze.txt\nOUTPUT_FILE=maze.txt")),
    ("triple_output_file_key", dict(OUTPUT_FILE="OUTPUT_FILE=a.txt\nOUTPUT_FILE=b.txt\nOUTPUT_FILE=c.txt")),
    ("output_file_leading_space_line", dict(OUTPUT_FILE=" OUTPUT_FILE=maze.txt")),
    ("output_file_multiple_leading_spaces_line", dict(OUTPUT_FILE="   OUTPUT_FILE=maze.txt")),
    ("output_file_at_sign_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE@=maze.txt")),
    ("output_file_ampersand_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE&=maze.txt")),
    ("output_file_slash_suffix_key", dict(OUTPUT_FILE="OUTPUT_FILE/=maze.txt")),

    # --- PERFECT invalid values ---
    ("perfect_invalid_word", dict(PERFECT="PERFECT=Yes")),
    ("perfect_lowercase_true", dict(PERFECT="PERFECT=true")),
    ("perfect_lowercase_false", dict(PERFECT="PERFECT=false")),
    ("perfect_numeric_one", dict(PERFECT="PERFECT=1")),
    ("perfect_empty_value", dict(PERFECT="PERFECT=")),

    # --- PERFECT type-related edge cases ---
    ("perfect_all_caps_true", dict(PERFECT="PERFECT=TRUE")),
    ("perfect_all_caps_false", dict(PERFECT="PERFECT=FALSE")),
    ("perfect_all_caps_yes", dict(PERFECT="PERFECT=YES")),
    ("perfect_lowercase_yes", dict(PERFECT="PERFECT=yes")),
    ("perfect_titlecase_no", dict(PERFECT="PERFECT=No")),
    ("perfect_all_caps_no", dict(PERFECT="PERFECT=NO")),
    ("perfect_lowercase_no", dict(PERFECT="PERFECT=no")),
    ("perfect_titlecase_on", dict(PERFECT="PERFECT=On")),
    ("perfect_all_caps_on", dict(PERFECT="PERFECT=ON")),
    ("perfect_lowercase_on", dict(PERFECT="PERFECT=on")),
    ("perfect_titlecase_off", dict(PERFECT="PERFECT=Off")),
    ("perfect_all_caps_off", dict(PERFECT="PERFECT=OFF")),
    ("perfect_lowercase_off", dict(PERFECT="PERFECT=off")),
    ("perfect_single_char_t", dict(PERFECT="PERFECT=T")),
    ("perfect_single_char_f", dict(PERFECT="PERFECT=F")),
    ("perfect_single_char_lower_t", dict(PERFECT="PERFECT=t")),
    ("perfect_single_char_lower_f", dict(PERFECT="PERFECT=f")),
    ("perfect_single_char_y", dict(PERFECT="PERFECT=Y")),
    ("perfect_single_char_n", dict(PERFECT="PERFECT=N")),
    ("perfect_single_char_lower_y", dict(PERFECT="PERFECT=y")),
    ("perfect_single_char_lower_n", dict(PERFECT="PERFECT=n")),
    ("perfect_numeric_zero", dict(PERFECT="PERFECT=0")),
    ("perfect_numeric_negative_one", dict(PERFECT="PERFECT=-1")),
    ("perfect_numeric_two", dict(PERFECT="PERFECT=2")),
    ("perfect_float_one", dict(PERFECT="PERFECT=1.0")),
    ("perfect_float_zero", dict(PERFECT="PERFECT=0.0")),
    ("perfect_zero_padded_one", dict(PERFECT="PERFECT=01")),
    ("perfect_true_trailing_dot", dict(PERFECT="PERFECT=True.")),
    ("perfect_false_trailing_dot", dict(PERFECT="PERFECT=False.")),
    ("perfect_true_trailing_bang", dict(PERFECT="PERFECT=True!")),
    ("perfect_false_trailing_question", dict(PERFECT="PERFECT=False?")),
    ("perfect_concatenated_true_false", dict(PERFECT="PERFECT=TrueFalse")),
    ("perfect_concatenated_false_true", dict(PERFECT="PERFECT=FalseTrue")),
    ("perfect_truncated_true", dict(PERFECT="PERFECT=Tru")),
    ("perfect_truncated_false", dict(PERFECT="PERFECT=Fals")),
    ("perfect_typo_flase", dict(PERFECT="PERFECT=Flase")),
    ("perfect_typo_treu", dict(PERFECT="PERFECT=Treu")),
    ("perfect_word_null_upper", dict(PERFECT="PERFECT=NULL")),
    ("perfect_word_null_lower", dict(PERFECT="PERFECT=null")),
    ("perfect_word_none", dict(PERFECT="PERFECT=None")),
    ("perfect_word_none_lower", dict(PERFECT="PERFECT=none")),
    ("perfect_word_nil", dict(PERFECT="PERFECT=nil")),
    ("perfect_word_undefined", dict(PERFECT="PERFECT=undefined")),
    ("perfect_word_void", dict(PERFECT="PERFECT=void")),
    ("perfect_word_enabled", dict(PERFECT="PERFECT=enabled")),
    ("perfect_word_disabled", dict(PERFECT="PERFECT=disabled")),
    ("perfect_word_enable", dict(PERFECT="PERFECT=Enable")),
    ("perfect_word_disable", dict(PERFECT="PERFECT=Disable")),
    ("perfect_true_and_false_joined_by_comma", dict(PERFECT="PERFECT=True,False")),
    ("perfect_true_and_false_joined_by_slash", dict(PERFECT="PERFECT=True/False")),

    # --- seed type-related edge cases ---
    # seed is `Optional[int]` with no explicit constraints, and pydantic's
    # lax int coercion accepts things like "1_000" or "  5  ", so these
    # cases stick to strings int() genuinely cannot interpret.
    ("seed_non_integer_word", dict(SEED="seed=abc")),
    ("seed_word_suffix", dict(SEED="seed=5abc")),
    ("seed_word_prefix", dict(SEED="seed=abc5")),
    ("seed_empty_value", dict(SEED="seed=")),
    ("seed_boolean_word_true", dict(SEED="seed=True")),
    ("seed_boolean_word_false", dict(SEED="seed=False")),
    ("seed_none_word", dict(SEED="seed=None")),
    ("seed_null_word", dict(SEED="seed=null")),
    ("seed_nan_lowercase", dict(SEED="seed=nan")),
    ("seed_nan_titlecase", dict(SEED="seed=NaN")),
    ("seed_infinity_word", dict(SEED="seed=Infinity")),
    ("seed_inf_lowercase", dict(SEED="seed=inf")),
    ("seed_negative_infinity", dict(SEED="seed=-inf")),
    ("seed_scientific_notation", dict(SEED="seed=1e2")),
    ("seed_scientific_notation_no_exponent_digits", dict(SEED="seed=1e")),
    ("seed_leading_e", dict(SEED="seed=e5")),
    ("seed_bare_e", dict(SEED="seed=e")),
    ("seed_float_with_fraction", dict(SEED="seed=1.5")),
    ("seed_float_with_fraction_trailing_zero", dict(SEED="seed=1.50")),
    ("seed_positive_float_with_plus", dict(SEED="seed=+5.5")),
    ("seed_negative_float", dict(SEED="seed=-0.5")),
    ("seed_double_dot", dict(SEED="seed=3..3")),
    ("seed_trailing_dot", dict(SEED="seed=5..")),
    ("seed_trailing_dot_single", dict(SEED="seed=1.")),
    ("seed_lone_dot", dict(SEED="seed=.")),
    ("seed_hex_value", dict(SEED="seed=0x1A")),
    ("seed_bare_hex_prefix", dict(SEED="seed=0x")),
    ("seed_binary_literal", dict(SEED="seed=0b101")),
    ("seed_bare_binary_prefix", dict(SEED="seed=0b")),
    ("seed_octal_literal", dict(SEED="seed=0o17")),
    ("seed_bare_octal_prefix", dict(SEED="seed=0o")),
    ("seed_long_suffix", dict(SEED="seed=5L")),
    ("seed_comma_thousands_separator", dict(SEED="seed=1,000")),
    ("seed_repeated_comma", dict(SEED="seed=5,,0")),
    ("seed_double_plus_sign", dict(SEED="seed=++5")),
    ("seed_double_minus_sign", dict(SEED="seed=--3")),
    ("seed_trailing_minus", dict(SEED="seed=3-")),
    ("seed_trailing_plus", dict(SEED="seed=3+")),
    ("seed_bare_plus", dict(SEED="seed=+")),
    ("seed_bare_minus", dict(SEED="seed=-")),
    ("seed_lone_plus_space", dict(SEED="seed=+ 5")),
    ("seed_internal_space", dict(SEED="seed=3 3")),
    ("seed_internal_tab", dict(SEED="seed=3\t3")),
    ("seed_arithmetic_expression_add", dict(SEED="seed=5+5")),
    ("seed_arithmetic_expression_sub", dict(SEED="seed=5-5")),
    ("seed_arithmetic_expression_div", dict(SEED="seed=20/2")),
    ("seed_arithmetic_expression_mul", dict(SEED="seed=20*1")),
    ("seed_percent_suffix", dict(SEED="seed=5%")),
    ("seed_percent_prefix", dict(SEED="seed=%5")),
    ("seed_parenthesized", dict(SEED="seed=(5)")),

    # --- Structural / syntax errors ---
    ("duplicate_width_key", dict(WIDTH="WIDTH=20\nWIDTH=30")),
    ("duplicate_height_key", dict(HEIGHT="HEIGHT=15\nHEIGHT=30")),
    ("duplicate_entry_key", dict(ENTRY="ENTRY=0,0\nENTRY=1,1")),
    ("duplicate_exit_key", dict(EXIT="EXIT=19,14\nEXIT=10,10")),
    ("duplicate_perfect_key", dict(PERFECT="PERFECT=True\nPERFECT=False")),
    ("duplicate_seed_key", dict(SEED="seed=1\nseed=2")),

    # --- seed key casing: CONFIG_OPTIONS registers "seed" lowercase only,
    # unlike every other key, so any other casing is an unknown key. ---
    ("seed_uppercase_key", dict(SEED="SEED=5")),
    ("seed_titlecase_key", dict(SEED="Seed=5")),
    ("unknown_key", dict(WIDTH="WIDTH=20\nFOOBAR=123")),
    ("lowercase_key_not_recognized", dict(WIDTH="width=20")),
    ("line_without_equals_sign", dict(WIDTH="WIDTHONLY")),

    # --- Regression: a line starting with a space must not crash the
    # parser when it is the very first line processed (before any `key`
    # variable has ever been assigned). Previously this raised an
    # uncaught UnboundLocalError instead of exiting gracefully with
    # "Invalid Input" (see parse.py's leading-space branch). ---
    ("leading_space_as_first_line", dict(WIDTH=" WIDTH=20")),
    ("leading_space_after_only_comments_and_blanks", dict(WIDTH="# a comment\n\n WIDTH=20")),

    # --- Boundary/decision-table interaction: WIDTH=0 and HEIGHT=0 pass the
    # field's own `ge=0` check, but leave no valid coordinate for the entry
    # (0 <= x <= width-1 becomes 0 <= x <= -1, an empty range), so the
    # overall config is always invalid despite the field itself parsing. ---
    ("width_zero_leaves_no_room_for_entry", dict(WIDTH="WIDTH=0")),
    ("height_zero_leaves_no_room_for_entry", dict(HEIGHT="HEIGHT=0")),
]

TESTS=373
assert len(INVALID_CASES) == TESTS, f"expected {TESTS} cases, got {len(INVALID_CASES)}"


@pytest.mark.parametrize(
    "overrides", [case for _, case in INVALID_CASES],
    ids=[name for name, _ in INVALID_CASES],
)
def test_invalid_config_exits_with_error(tmp_path: Path, overrides: dict[Any, Any]) -> None:
    content = build_config(**overrides)
    exc_info = run_arg_parse(tmp_path, content)
    assert exc_info.value.code == 1


def test_missing_config_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "does_not_exist.txt"
    sys.argv = ["a_maze_ing.py", str(missing_path)]
    with pytest.raises(SystemExit):
        arg_parse()


def test_directory_as_config_file_exits_gracefully(tmp_path: Path) -> None:
    sys.argv = ["a_maze_ing.py", str(tmp_path)]
    with pytest.raises(SystemExit) as exc_info:
        arg_parse()
    assert exc_info.value.code == 1


def test_empty_config_file_is_rejected(tmp_path: Path) -> None:
    exc_info = run_arg_parse(tmp_path, "")
    assert exc_info.value.code == 1


def test_config_file_with_only_comments_and_blank_lines_is_rejected(
    tmp_path: Path,
) -> None:
    content = "# just a comment\n\n\n# another comment\n"
    exc_info = run_arg_parse(tmp_path, content)
    assert exc_info.value.code == 1


# --- Error message content ---
#
# The other invalid-input tests only assert exit code 1; the module
# docstring also promises "printing a clear error message". These tests
# cover the three branches of parse.py's _format_validation_error:
#   - field-level pydantic error (loc is non-empty, e.g. ("width",))
#     -> "{msg}: {LOC}" with the field name upper-cased
#   - "seed" is the one field kept lower-case in that message
#   - model_validator(mode="after") errors have an empty loc (the error is
#     raised on the model, not a field) -> the bare message with no suffix


def test_field_level_error_message_includes_uppercased_field_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    exc_info = run_arg_parse(tmp_path, build_config(WIDTH="WIDTH=abc"))
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert out.strip().endswith(": WIDTH")


def test_seed_error_message_keeps_seed_lowercase(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    exc_info = run_arg_parse(tmp_path, build_config(SEED="seed=abc"))
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert out.strip().endswith(": seed")


def test_model_validator_error_message_has_no_field_suffix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    # ENTRY out of bounds is rejected by validate_entry_and_exit, a
    # model_validator(mode="after"): its ValidationError has an empty loc,
    # so _format_validation_error must not append a ": FIELD" suffix.
    exc_info = run_arg_parse(tmp_path, build_config(ENTRY="ENTRY=25,0"))
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert out.strip() == "Invalid 'ENTRY'"


def test_structural_parse_error_message_has_no_field_suffix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    # A raw ParseError raised outside pydantic (here: an unrecognized key)
    # is printed as-is by the bare `except (ParseError, OSError)` branch,
    # with no ": FIELD" suffix formatting applied.
    exc_info = run_arg_parse(
        tmp_path, build_config(WIDTH="WIDTH=20\nFOOBAR=123"),
    )
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert out.strip() == "Invalid Key: FOOBAR"


