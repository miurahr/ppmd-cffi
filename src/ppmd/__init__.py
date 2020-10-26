from typing import BinaryIO

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

__copyright__ = 'Copyright (C) 2020 Hiroshi Miura'

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no-cover
    # package is not installed
    __version__ = "unknown"

from _ppmd import ffi, lib  # type: ignore  # noqa

_PPMD7_MIN_ORDER = 2
_PPMD7_MAX_ORDER = 64

_PPMD7_MIN_MEM_SIZE = 1 << 11
_PPMD7_MAX_MEM_SIZE = 0xFFFFFFFF - 12 * 3


@ffi.def_extern()
def dst_write(b: bytes, size: int, userdata: object) -> None:
    encoder = ffi.from_handle(userdata)
    buf = ffi.buffer(b, size)
    encoder.destination.write(buf)


@ffi.def_extern()
def src_readinto(b: bytes, size: int, userdata: object) -> int:
    decoder = ffi.from_handle(userdata)
    buf = ffi.buffer(b, size)
    result = decoder.source.readinto(buf)
    return result


class PpmdEncoder:

    def __init__(self, destination: BinaryIO, max_order: int, mem_size: int):
        self.closed = False
        self.flushed = False
        self.destination = destination
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeEnc *')
        self.writer = ffi.new('RawWriter *')
        self._userdata = ffi.new_handle(self)
        if _PPMD7_MIN_ORDER <= max_order <= _PPMD7_MAX_ORDER and _PPMD7_MIN_MEM_SIZE <= mem_size <= _PPMD7_MAX_MEM_SIZE:
            lib.ppmd_state_init(self.ppmd, max_order, mem_size)
            lib.ppmd_compress_init(self.rc, self.writer, lib.dst_write, self._userdata)
        else:
            raise ValueError("PPMd wrong parameters.")

    def encode(self, inbuf) -> None:
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


class PpmdDecoder:

    def __init__(self, source: BinaryIO, max_order: int, mem_size: int):
        if not source.readable:
            raise ValueError
        self.source = source
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        self.reader = ffi.new('RawReader *')
        self.max_order = max_order  # type: int
        self.mem_size = mem_size  # type: int
        self.initialized = False
        self.closed = False

    def _init2(self):
        self._userdata = ffi.new_handle(self)
        lib.ppmd_state_init(self.ppmd, self.max_order, self.mem_size)
        lib.ppmd_decompress_init(self.rc, self.reader, lib.src_readinto, self._userdata)

    def decode(self, length) -> bytes:
        if not self.initialized:
            self._init2()
            self.initialized = True
        outbuf = bytearray()
        for _ in range(length):
            sym = lib.Ppmd7_DecodeSymbol(self.ppmd, self.rc)
            outbuf += sym.to_bytes(1, 'little')
        if self.rc.Code != 0:
            pass
        return bytes(outbuf)

    def close(self):
        if self.closed:
            return
        lib.ppmd_state_close(self.ppmd)
        ffi.release(self.ppmd)
        ffi.release(self.reader)
        ffi.release(self.rc)
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, types, value, traceback):
        self.close()
