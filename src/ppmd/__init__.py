import argparse
import array
import io
import mmap
import pathlib
import struct
from typing import Any, BinaryIO, Optional, Union

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore  # noqa

__copyright__ = 'Copyright (C) 2020 Hiroshi Miura'

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no-cover
    # package is not installed
    __version__ = "unknown"

from _ppmd import ffi, lib  # type: ignore  # noqa

MAGIC = 0x84ACAF8F
READ_BLOCKSIZE = 16384

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


class PpmdBuffer(io.BufferedIOBase):

    def __init__(self):
        self._buf = bytearray()

    def writable(self):
        return True

    def write(self, b: Union[bytes, bytearray, memoryview, array.array, mmap.mmap]):
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

    def tell(self):
        return 0

    @property
    def size(self):
        return len(self._buf)


class PpmdEncoder:

    def __init__(self, destination: Union[BinaryIO, PpmdBuffer], max_order: int, mem_size: int):
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


class PpmdBufferEncoder:

    def __init__(self, level: int, mem: int):
        self.buf = PpmdBuffer()
        self._encoder = PpmdEncoder(self.buf, level, mem)
        self.closed = False
        self.flushed = False

    def encode(self, data: Union[bytes, bytearray, memoryview]) -> bytes:
        self._encoder.encode(data)
        result = self.buf.read()
        return result

    def flush(self) -> bytes:
        if self.flushed:
            return b''
        self._encoder.flush()
        result = self.buf.read()
        self.flushed = True
        return result

    def close(self) -> None:
        if self.closed:
            return
        self._encoder.close()
        del self.buf
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.flushed:
            self.flush()
        self.close()


class PpmdDecoder:

    def __init__(self, source: Union[BinaryIO, PpmdBuffer], max_order: int, mem_size: int):
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

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class PpmdBufferDecoder:

    def __init__(self, level: int, mem: int):
        self.buf = PpmdBuffer()
        self._decoder = PpmdDecoder(self.buf, level, mem)
        self.closed = False

    def decode(self, data: bytes, size: int) -> bytes:
        if len(data) > 0:
            self.buf.write(data)
            result = bytearray()
            while self.buf.size > 0 and len(result) < size:
                result += self._decoder.decode(1)
            return bytes(result)
        else:
            return self._decoder.decode(size)

    def close(self):
        self._decoder.close()
        if self.closed:
            return
        del self.buf
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Ppmd8Decoder:

    def __init__(self, source: BinaryIO, max_order: int, mem_size: int, restore: int):
        self.closed = False
        self.source = source
        self.ppmd = ffi.new('CPpmd8 *')
        self.reader = ffi.new('RawReader *')
        self._userdata = ffi.new_handle(self)
        self.max_order = max_order  # type: int
        self.mem_size = mem_size  # type: int
        self.restore = restore  # type: int
        lib.ppmd8_decompress_init(self.ppmd, self.reader, lib.src_readinto, self._userdata)
        lib.Ppmd8_Construct(self.ppmd)
        lib.ppmd8_malloc(self.ppmd, mem_size << 20)
        lib.Ppmd8_RangeDec_Init(self.ppmd)
        lib.Ppmd8_Init(self.ppmd, max_order, restore)

    def decode(self, length):
        outbuf = bytearray()
        for _ in range(length):
            sym = lib.Ppmd8_DecodeSymbol(self.ppmd)
            if sym < 0:
                break
            outbuf += sym.to_bytes(1, 'little')
        if self.ppmd.Code != 0:
            pass  # FIXME
        return bytes(outbuf)

    def close(self):
        if not self.closed:
            lib.ppmd8_mfree(self.ppmd)
            ffi.release(self.ppmd)
            ffi.release(self.reader)
            self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Ppmd8Encoder:

    def __init__(self, destination: BinaryIO, max_order: int, mem_size: int, restore: int):
        self.closed = False
        self.flushed = False
        self.destination = destination
        self.ppmd = ffi.new('CPpmd8 *')
        self.writer = ffi.new('RawWriter *')
        self._userdata = ffi.new_handle(self)
        lib.ppmd8_compress_init(self.ppmd, self.writer, lib.dst_write, self._userdata)
        lib.Ppmd8_Construct(self.ppmd)
        lib.ppmd8_malloc(self.ppmd, mem_size << 20)
        # lib.Ppmd8_RangeEnc_Init(self.ppmd)  # this is defined as macro
        self.ppmd.Low = 0
        self.ppmd.Range = 0xFFFFFFFF
        lib.Ppmd8_Init(self.ppmd, max_order, restore)

    def encode(self, inbuf) -> None:
        for sym in inbuf:
            lib.Ppmd8_EncodeSymbol(self.ppmd, sym)

    def flush(self):
        if not self.flushed:
            lib.Ppmd8_EncodeSymbol(self.ppmd, -1)  # endmark
            lib.Ppmd8_RangeEnc_FlushData(self.ppmd)
            self.flushed = True

    def close(self):
        if not self.closed:
            lib.ppmd8_mfree(self.ppmd)
            self.closed = True
            ffi.release(self.ppmd)
            ffi.release(self.writer)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class PpmdHeader:

    size = 16

    def __init__(self):
        self.attr = 0x80
        self.info = 8 << 12
        self.fnlen = 1
        self.restore = 0
        self.version = 8

    def read(self, file):
        if struct.unpack("<I", file.read(4))[0] != MAGIC:
            raise ValueError("Invalid header {}\n".format(self.magic))
        self.attr = struct.unpack("<I", file.read(4))[0]
        self.info = struct.unpack("<H", file.read(2))[0]
        self.version = self.info >> 12
        fn_len = struct.unpack("<H", file.read(2))[0]
        self.restore = fn_len >> 14
        file.read(2)
        file.read(2)
        file.read(fn_len & 0x1FF)

    def write(self, file, order, mem, restore):
        self.info = (self.version << 12) | ((mem - 1) << 4) | (order - 1) & 0x0f
        self.fnlen = 1 | (restore << 14)
        file.write(struct.pack("<I", MAGIC))
        file.write(struct.pack("<I", self.attr))
        file.write(struct.pack("<H", self.info))
        file.write(struct.pack("<H", self.fnlen))
        file.write(b'\x00\x00')
        file.write(b'\x00\x00')
        file.write(b'a')

    def __len__(self):
        return self.size


class Ppmd8Decompressor:

    def __init__(self, file, filesize):
        hdr = PpmdHeader()
        hdr.read(file)
        restore = hdr.restore
        order = (hdr.info & 0x0f) + 1
        mem = ((hdr.info >> 4) & 0xff) + 1
        self.decoder = Ppmd8Decoder(file, order, mem, restore)
        self.file = file
        self.size = filesize

    def decompress(self, ofile):
        while self.file.tell() < self.size:
            data = self.decoder.decode(READ_BLOCKSIZE)
            if len(data) == 0:
                break
            ofile.write(data)

    def close(self):
        self.decoder.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self


class Ppmd8Compressor:

    def __init__(self, ofile, order, mem):
        PpmdHeader().write(ofile, order, mem, 0)
        self.encoder = Ppmd8Encoder(ofile, order, mem, 0)

    def compress(self, src):
        data = src.read(READ_BLOCKSIZE)
        while len(data) > 0:
            self.encoder.encode(data)
            data = src.read(READ_BLOCKSIZE)
        self.encoder.flush()

    def close(self):
        self.encoder.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self


def main(arg: Optional[Any] = None):
    parser = argparse.ArgumentParser(prog='ppmd', description='ppmd')
    parser.add_argument("-x", action="store_true")
    parser.add_argument("target")
    args = parser.parse_args(arg)
    targetfile = pathlib.Path(args.target)
    if args.x:
        if targetfile.suffix != '.ppmd':
            print("Target file does not have .ppmd suffix.")
            exit(1)
        target_size = targetfile.stat().st_size
        parent = targetfile.parent
        extractedfile = pathlib.Path(parent.joinpath(targetfile.stem))
        with extractedfile.open('wb') as ofile:
            with targetfile.open('rb') as target:
                with Ppmd8Decompressor(target, target_size) as decompressor:
                    decompressor.decompress(ofile)
    else:
        archivefile = pathlib.Path(str(targetfile) + '.ppmd')
        with archivefile.open('wb') as target:
            with targetfile.open('rb') as src:
                with Ppmd8Compressor(target, 6, 8) as compressor:
                    compressor.compress(src)
