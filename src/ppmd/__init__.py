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

from _ppmd import ffi, lib

BUFFER_SIZE = 1048576


class PpmdEncoder:

    def __init__(self, level: int, mem: int):
        self.closed = False
        self.flushed = False
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeEnc *')
        self.writer = ffi.new('BufferWriter *')
        self.buf = ffi.new('char []', BUFFER_SIZE)
        self.writer.buf = self.buf
        self.writer.size = BUFFER_SIZE
        max_order = level
        mem_size = mem << 20
        lib.ppmd_state_init(self.ppmd, max_order, mem_size)
        lib.ppmd_compress_init(self.rc, self.writer)

    def encode(self, inbuf):
        for sym in inbuf:
            lib.Ppmd7_EncodeSymbol(self.ppmd, self.rc, sym)
        result = ffi.buffer(self.buf)[:self.writer.pos]
        self.writer.pos = 0
        return result

    def flush(self):
        if self.flushed:
            return
        self.flushed = True
        lib.Ppmd7z_RangeEnc_FlushData(self.rc)
        result = ffi.buffer(self.buf)[:self.writer.pos]
        return result

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


class PpmdDecoder:

    def __init__(self, source: BinaryIO, level: int, mem: int):
        if not source.readable:
            raise ValueError
        self.source = source
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        self.reader = ffi.new('BufferReader *')
        self._userdata = ffi.new_handle(self)
        self.max_order = level
        self.mem_size = mem << 20
        lib.ppmd_state_init(self.ppmd, self.max_order, self.mem_size)
        lib.ppmd_decompress_init(self.rc, self.reader, lib.src_readinto, self._userdata)

    def decode(self, length):
        outbuf = bytearray()
        for _ in range(length):
            sym = lib.Ppmd7_DecodeSymbol(self.ppmd, self.rc)
            outbuf += sym.to_bytes(1, 'little')
        if self.rc.Code != 0:
            pass
        return bytes(outbuf)

    def close(self):
        lib.ppmd_state_close(self.ppmd)
        ffi.release(self.ppmd)
        ffi.release(self.reader)
        ffi.release(self.rc)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


@ffi.def_extern()
def src_readinto(b: bytes, size: int, userdata: object) -> int:
    decoder = ffi.from_handle(userdata)
    buf = ffi.buffer(b, size)
    result = decoder.source.readinto(buf)
    return result
