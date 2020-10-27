import datetime
import pathlib
import struct

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

from . import Ppmd8Decoder, Ppmd8Encoder

__copyright__ = 'Copyright (C) 2020 Hiroshi Miura'
MAGIC = 0x84ACAF8F


class PpmdHeader:

    size = 16

    def __init__(self):
        self.magic = None
        self.attr = None
        self.info = None
        self.fnlen = None
        self.date = None
        self.time = None

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
        self.date = struct.unpack("<H", file.read(2))
        self.time = struct.unpack("<H", file.read(2))
        self.filename = file.read(fnlen & 0x1FF).decode('UTF-8')

    def write(self, file):
        file.write(struct.pack("<I", self.magic))
        file.write(struct.pack("<I", self.attr))
        file.write(struct.pack("<H", self.info))
        fname = self.filename.encode('UTF-8')
        fnlen = len(fname) | self.restore << 14
        file.write(struct.pack("<H", fnlen))
        file.write(struct.pack("<H", self.date))
        file.write(struct.pack("<H", self.time))

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

    def decompress(self) -> bytes:
        buf = self.decoder.decompress(1)
        while len(buf) > 0 and not self.file.eof:
            buf += self.decoder.decompress(1)

    def close(self):
        self.decoder.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self


class Ppmd8Compressor:

    def __init__(self, file, order, mem, targetpath):
        hdr = PpmdHeader()
        hdr.magic = MAGIC
        hdr.info = (mem - 1) << 4 + (order - 1) & 0x0f
        hdr.attr = 0
        self.filename = targetpath.basename
        dt = datetime.fromtimestamp(targetpath.stat().st_mtime, datetime.timezone.utc)
        hdr.date = dt.date()
        hdr.time = dt.time()
        fname = self.filename.encode("UTF-8")
        hdr.fnlen = len(fname) & 0x1ff
        hdr.write(file)
        self.encoder = Ppmd8Encoder(file, order, mem, 0)

    def compress(self, data):
        return self.encoder.encode(data)

    def flush(self):
        self.encoder.flush()

    def close(self):
        self.encoder.close()
