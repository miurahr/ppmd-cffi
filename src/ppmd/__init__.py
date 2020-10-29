import argparse
import pathlib
import struct
import sys
from typing import Any, BinaryIO, Optional

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

PPMD_HEADER_MAGIC = 0x84ACAF8F
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
        self.ppmd = ffi.new('CPpmd7 *')
        lib.ppmd_state_init(self.ppmd, max_order, mem_size)
        self.rc = ffi.new('CPpmd7z_RangeDec *')
        self.reader = ffi.new('RawReader *')
        self.source = source  # read indirectly through self._userdata
        self._userdata = ffi.new_handle(self)
        self.closed = False
        lib.ppmd_decompress_init(self.rc, self.reader, lib.src_readinto, self._userdata)

    def decode(self, length) -> bytes:
        b = bytearray()
        for _ in range(length):
            sym = lib.Ppmd7_DecodeSymbol(self.ppmd, self.rc)
            b += sym.to_bytes(1, 'little')
        if self.rc.Code != 0:
            pass  # FIXME
        return bytes(b)

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

    def __init__(self, version=8):
        self.attr = 0x80
        self.info = 8 << 12
        self.fnlen = 1
        self.restore = 0
        self.version = version

    def read(self, file):
        magic = struct.unpack("<I", file.read(4))[0]
        if magic != PPMD_HEADER_MAGIC:
            raise ValueError("Invalid header {}\n".format(magic))
        self.attr = struct.unpack("<I", file.read(4))[0]
        self.info = struct.unpack("<H", file.read(2))[0]
        self.version = self.info >> 12
        fn_len = struct.unpack("<H", file.read(2))[0]
        self.restore = fn_len >> 14
        file.read(2)
        file.read(2)
        file.read(fn_len & 0x1FF)

    def write(self, file, order, mem, restore=0):
        self.info = (self.version << 12) | ((mem - 1) << 4) | (order - 1) & 0x0f
        if self.version == 8:
            self.fnlen = 1 | (restore << 14)
        else:
            self.fnlen = 1
        file.write(struct.pack("<I", PPMD_HEADER_MAGIC))
        file.write(struct.pack("<I", self.attr))
        file.write(struct.pack("<H", self.info))
        file.write(struct.pack("<H", self.fnlen))
        file.write(b'\x00\x00')
        file.write(b'\x00\x00')
        file.write(b'a')

    def __len__(self):
        return self.size


class PpmdDecompressor:

    def __init__(self, file, filesize):
        hdr = PpmdHeader()
        hdr.read(file)
        restore = hdr.restore
        order = (hdr.info & 0x0f) + 1
        mem = ((hdr.info >> 4) & 0xff) + 1
        if hdr.version == 8:
            self.decoder = Ppmd8Decoder(file, order, mem, restore)
        elif hdr.version == 7:
            self.decoder = Ppmd7Decoder(file, order, mem)
        else:
            raise ValueError("Unsupported PPMd version detected.")
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


class PpmdCompressor:

    def __init__(self, ofile, order, mem, version=8):
        if version == 7:
            PpmdHeader(version=7).write(ofile, order, mem)
            self.encoder = Ppmd7Encoder(ofile, order, mem)
        elif version == 8:
            PpmdHeader(version=8).write(ofile, order, mem, 0)
            self.encoder = Ppmd8Encoder(ofile, order, mem, 0)
        else:
            raise ValueError("Unsupported PPMd version.")

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


Ppmd8Decompressor = PpmdDecompressor
Ppmd8Compressor = PpmdCompressor


def main(arg: Optional[Any] = None):
    parser = argparse.ArgumentParser(prog='ppmd', description='ppmd')
    parser.add_argument("-x", action="store_true", help="Specify decompression")
    parser.add_argument("-c", action="store_true", help="Output to stdout")
    parser.add_argument("-7", "--seven", action="store_true", help="Compress with PPMd ver.H instead of Ver.I")
    parser.add_argument("target")
    args = parser.parse_args(arg)
    targetfile = pathlib.Path(args.target)
    if args.x:
        if targetfile.suffix != '.ppmd':
            sys.stderr.write("Target file does not have .ppmd suffix.")
            exit(1)
        if args.seven:
            sys.stderr.write("Cannot specify version for extraction.")
            exit(1)
        target_size = targetfile.stat().st_size
        if args.c:
            with targetfile.open('rb') as target:
                with PpmdDecompressor(target, target_size) as decompressor:
                    sys.stdout.flush()
                    decompressor.decompress(sys.stdout.buffer)
                    sys.stdout.buffer.flush()
        else:
            parent = targetfile.parent
            extractedfile = pathlib.Path(parent.joinpath(targetfile.stem))
            with extractedfile.open('wb') as ofile:
                with targetfile.open('rb') as target:
                    with PpmdDecompressor(target, target_size) as decompressor:
                        decompressor.decompress(ofile)
    else:
        archivefile = pathlib.Path(str(targetfile) + '.ppmd')
        with archivefile.open('wb') as target:
            with targetfile.open('rb') as src:
                if args.seven:
                    with PpmdCompressor(target, 6, 16, version=7) as compressor:
                        compressor.compress(src)
                else:
                    with PpmdCompressor(target, 6, 8, version=8) as compressor:
                        compressor.compress(src)
