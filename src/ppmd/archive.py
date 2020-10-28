import datetime
import struct

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

from . import Ppmd8Decoder, Ppmd8Encoder

__copyright__ = 'Copyright (C) 2020 Hiroshi Miura'
MAGIC = 0x84ACAF8F
READ_BLOCKSIZE = 16384


class PpmdHeader:

    size = 16

    def __init__(self):
        self.magic = None
        self.attr = None
        self.info = None
        self.fnlen = None

    def read(self, file):
        self.magic = struct.unpack("<I", file.read(4))
        if self.magic != MAGIC:
            raise ValueError("Invalid header")
        self.attr = struct.unpack("<I", file.read(4))
        self.info = struct.unpack("<H", file.read(2))
        if self.info >> 12 != 'I' - 'A':
            raise ValueError("Invalid header")
        fnlen = struct.unpack("<H", file.read(2))
        self.restore = fnlen >> 14
        _ = struct.unpack("<H", file.read(2))
        _ = struct.unpack("<H", file.read(2))
        _ = file.read(fnlen & 0x1FF).decode('UTF-8')

    def write(self, file):
        file.write(struct.pack("<I", self.magic))
        file.write(struct.pack("<I", self.attr))
        file.write(struct.pack("<H", self.info))
        file.write(struct.pack("<H", self.fnlen))
        file.write(struct.pack("<H", 0))
        file.write(struct.pack("<H", 0))
        file.write(struct.pack("<H", b'a'))

    def __len__(self):
        return self.size


class Ppmd8Decompressor:

    def __init__(self, file):
        hdr = PpmdHeader()
        hdr.read(file)
        restore = hdr.restore
        order = (hdr.info & 0x0f) + 1
        mem = (((hdr.info >> 4) & 0xff) + 1) << 20
        self.decoder = Ppmd8Decoder(file, order, mem, restore)
        self.file = file
        return hdr.filename, hdr.date, hdr.time

    def decompress(self, ofile):
        while not self.file.eof:
            ofile.write(self.decoder.decompress())

    def close(self):
        self.decoder.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self


class Ppmd8Compressor:

    def __init__(self, ofile, order, mem):
        hdr = PpmdHeader()
        hdr.magic = MAGIC
        hdr.info = (mem - 1) << 4 + (order - 1) & 0x0f
        hdr.attr = 0
        hdr.fnlen = 1
        hdr.write(ofile)
        self.encoder = Ppmd8Encoder(ofile, order, mem, 0)

    def compress(self, src):
        data = src.read(READ_BLOCKSIZE)
        while len(data) > 0:
            self.encoder.encode(data)
            data = src.read(READ_BLOCKSIZE)
        self.encoder.flush()

    def close(self):
        self.encoder.close()
