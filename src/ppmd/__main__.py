import argparse
import pathlib
from typing import Any, Optional

from . import archive


def main(arg: Optional[Any] = None):
    parser = argparse.ArgumentParser(prog='ppmd', description='ppmd')
    parser.add_argument("-x", action="store_true")
    parser.add_argument("target")
    args = parser.parse_args(arg)
    targetfile = pathlib.Path(args.target)
    if args.x:
        extractedfile = pathlib.Path(str(targetfile) + '.orig')
        with extractedfile.open('wb') as ofile:
            with targetfile.open('rb') as target:
                with archive.Ppmd8Decompressor(target) as decompressor:
                    decompressor.decomress(ofile)
    else:
        archivefile = pathlib.Path(str(targetfile) + '.ppmd')
        with archivefile.open('wb') as target:
            with targetfile.open('rb') as src:
                with archive.Ppmd8Compressor(target, 6, 8) as compressor:
                    compressor.compress(src)


if __name__ == "__main__":
    main()
