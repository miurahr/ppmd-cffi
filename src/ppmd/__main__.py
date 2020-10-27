import argparse
import pathlib
import sys
from typing import Any, Optional

from . import archive


def main(arg: Optional[Any] = None) -> int:
    parser = argparse.ArgumentParser(prog='ppmd', description='ppmd')
    parser.add_argument("-x", action="store_true")
    parser.add_argument("arcfile")
    args = parser.parse_args(arg)
    if args.x:
        target = args.arcfile
        targetfile = pathlib.Path(target)
        decompressor = archive.Ppmd8Decompressor(target)
        decompressor.decomress()

if __name__ == "__main__":
    sys.exit(main())
