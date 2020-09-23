import cffi
import pathlib
import sys


def is_64bit() -> bool:
    return sys.maxsize > 2**32


SOURCES = ['Ppmd8.c', 'Ppmd8Dec.c', 'Ppmd8Enc.c', 'ppmd-mini.c']
SRC_ROOT = pathlib.Path(__file__).parent.parent
sources = [SRC_ROOT.joinpath(s).as_posix() for s in SOURCES]

ffibuilder = cffi.FFI()

ffibuilder.set_source('_ppmd', r'''
''', sources=sources, include_dirs=[SRC_ROOT])


if __name__ == "__main__":    # not when running with setuptools
    ffibuilder.compile(verbose=True)
