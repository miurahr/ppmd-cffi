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


class Encoder:

    def __init__(self, fileobj: BinaryIO, level: int, mem: int):
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeEnc *')
        max_order = level
        mem_size = mem << 20
        lib.ppmd_state_init(self.ppmd, max_order, mem_size)
        lib.ppmd_compress_init(self.rc, fileobj)

    def encode(self, inbuf):
        for sym in inbuf:
            lib.Ppmd7_EncodeSymbol(self.ppmd, self.rc, sym)

    def flush(self):
        lib.Ppmd7_FlushData(self.rc)

    def close(self):
        lib.ppmd_state_close(self.ppmd)
        ffi.release(self.ppmd)
        ffi.release(self.rc)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()


class Decoder:

    def __init__(self, fileobj: BinaryIO, level: int, mem: int):
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        max_order = level
        mem_size = mem << 20
        lib.ppmd_state_init(self.ppmd, max_order, mem_size)
        lib.ppmd_decompress_init(self.rc, fileobj)

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
        lib.ppmd_state_close(self.ppmd)
        ffi.release(self.ppmd)
        ffi.release(self.rc)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
