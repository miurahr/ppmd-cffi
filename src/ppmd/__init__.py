import weakref
from typing import BinaryIO

try:
    from importlib.metadata import PackageNotFoundError, version  # type: ignore
except ImportError:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

__copyright__ = 'Copyright (C) 2020 Hiroshi Miura'

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no-cover
    # package is not installed
    __version__ = "unknown"

from _ppmd import ffi
from _ppmd import lib

global_weakkeydict = weakref.WeakKeyDictionary()


class Encoder:

    def __init__(self, level: int):
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        max_order = level
        mem_size = 16 << 20
        res = lib.ppmd_state_init(max_order, mem_size, self.ppmd)
        if res < 0:
            raise ValueError

    def encode(self, inbuf: bytes):
        buf = ffi.from_buffer(inbuf)
        res = ffi.buffer(buf)
        return res


class Decoder:

    def __init__(self, fileobj: BinaryIO, level: int, mem: int):
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        max_order = level
        mem_size = mem << 20
        lib.ppmd_state_init(max_order, mem_size, self.ppmd)
        lib.ppmd_decompress_init(fileobj, self.rc)

    def decode(self, size):
        outbuf = bytearray()
        for i in range(size):
            sym = lib.Ppmd7_DecodeSymbol(self.ppmd, self.rc)
            if sym < 0:
                break
            outbuf.append(sym)
        if self.rc.code != 0:
            raise ValueError
        return outbuf

    def close(self):
        lib.ppmd_decompress_close(self.ppmd)
        ffi.release(self.ppmd)
        ffi.release(self.rc)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
