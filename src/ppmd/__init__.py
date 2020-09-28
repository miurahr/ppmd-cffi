import io
from typing import BinaryIO, Optional, Union

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

from _ppmd import ffi, lib  # type: ignore  # noqa


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


class PpmdBuffer(io.BufferedIOBase):

    def __init__(self):
        self._buf = bytearray()

    def writable(self):
        return True

    def write(self, b: Union[bytes, bytearray, memoryview]):
        self._buf += b

    def readable(self):
        return True

    def read(self, size: Optional[int] = -1):
        if size is None or size < 0:
            length: int = len(self._buf)
        else:
            length = size
        result = self._buf[:length]
        self._buf[:] = self._buf[length:]
        return result

    def readinto(self, b) -> int:
        length = min(len(self._buf), len(b))
        b[:] = self._buf[:length]
        self._buf[:] = self._buf[length:]
        return length


class PpmdEncoder:

    def __init__(self, destination: Union[BinaryIO, PpmdBuffer], level: int, mem: int):
        self.closed = False
        self.flushed = False
        self.destination = destination
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeEnc *')
        self.writer = ffi.new('RawWriter *')
        self._userdata = ffi.new_handle(self)
        max_order = level
        mem_size = mem << 20
        lib.ppmd_state_init(self.ppmd, max_order, mem_size)
        lib.ppmd_compress_init(self.rc, self.writer, lib.dst_write, self._userdata)

    def encode(self, inbuf):
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


class PpmdBufferEncoder(PpmdEncoder):

    def __init__(self, level: int, mem: int):
        self.buf = PpmdBuffer()
        super(PpmdBufferEncoder, self).__init__(self.buf, level, mem)
        self.closed = False
        self.flushed = False

    def encode(self, data):
        super(PpmdBufferEncoder, self).encode(data)
        result = self.buf.read()
        return result

    def flush(self):
        if self.flushed:
            return b''
        super(PpmdBufferEncoder, self).flush()
        result = self.buf.read()
        self.flushed = True
        return result

    def close(self):
        if self.closed:
            return
        super(PpmdBufferEncoder, self).close()
        del self.buf
        self.closed = True


class PpmdDecoder:

    def __init__(self, source: Union[BinaryIO, PpmdBuffer], level: int, mem: int):
        if not source.readable:
            raise ValueError
        self.source = source
        self.ppmd = ffi.new('CPpmd7 *')
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        self.reader = ffi.new('RawReader *')
        self.max_order = level
        self.mem_size = mem << 20
        self.initialized = False
        self.closed = False

    def _init2(self):
        self._userdata = ffi.new_handle(self)
        lib.ppmd_state_init(self.ppmd, self.max_order, self.mem_size)
        lib.ppmd_decompress_init(self.rc, self.reader, lib.src_readinto, self._userdata)

    def decode(self, length):
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

    def __exit__(self, type, value, traceback):
        self.close()


class PpmdBufferDecoder(PpmdDecoder):

    def __init__(self, level: int, mem: int):
        self.buf = PpmdBuffer()
        super(PpmdBufferDecoder, self).__init__(self.buf, level, mem)
        self.closed = False

    def decode(self, data, size):
        self.buf.write(data)
        result = super(PpmdBufferDecoder, self).decode(size)
        return result

    def close(self):
        super(PpmdBufferDecoder, self).close()
        if self.closed:
            return
        del self.buf
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
