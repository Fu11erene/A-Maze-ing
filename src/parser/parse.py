import argparse
import sys


def arg_parse() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument("filename", type=open, help="設定ファイル")

    try:
        args = parser.parse_args()
        print([entry.strip()
              for entry in args.filename.readlines() if entry[0] != "#"])
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
