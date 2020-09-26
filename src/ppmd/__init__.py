import os
from typing import BinaryIO, Union

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
        self.closed = False
        self.flushed = False
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeEnc *')
        self.writer = ffi.new('CharWriter *')
        self.writer.fp = ffi.cast("FILE *", fileobj)
        max_order = level
        mem_size = mem << 20
        lib.ppmd_state_init(self.ppmd, max_order, mem_size)
        lib.ppmd_compress_init(self.rc, self.writer)

    def encode(self, inbuf: Union[bytes, bytearray, memoryview]):
        for sym in inbuf:
            lib.Ppmd7_EncodeSymbol(self.ppmd, self.rc, sym)

    def flush(self):
        if self.flushed:
            return
        self.flushed = True
        lib.Ppmd7z_RangeEnc_FlushData(self.rc)

    def close(self):
        if self.closed:
            return
        self.closed = True
        lib.ppmd_state_close(self.ppmd)
        ffi.release(self.ppmd)
        ffi.release(self.writer)
        ffi.release(self.rc)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not self.flushed:
            self.flush()
        self.close()


class Decoder:

    def __init__(self, fileobj: BinaryIO, level: int, mem: int):
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        self.reader = ffi.new('CharReader *')
        self.reader.fp = ffi.cast("FILE *", fileobj)
        max_order = level
        mem_size = mem << 20
        lib.ppmd_state_init(self.ppmd, max_order, mem_size)
        lib.ppmd_decompress_init(self.rc, self.reader)

    def decode(self, size):
        outbuf = bytearray()
        for i in range(size):
            sym = lib.Ppmd7_DecodeSymbol(self.ppmd, self.rc)
            if sym < 0:
                break
            outbuf.append(sym)
        if self.rc.Code != 0:
            pass
        return outbuf

    def close(self):
        lib.ppmd_state_close(self.ppmd)
        ffi.release(self.ppmd)
        ffi.release(self.reader)
        ffi.release(self.rc)

    def __enter__(self):
        return self

    def __exit__(self ,type, value, traceback):
        self.close()
