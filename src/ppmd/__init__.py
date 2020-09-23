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

BUFFER_LENGTH = 8192


class Encoder:

    def __init__(self):
        pass

    def encode(self, inbuf: bytes):
        buf = ffi.from_buffer(inbuf)
        res = ffi.buffer(buf)
        return res


class Decoder:
    def __init__(self):
        pass

    def decode(self, inbuf: bytes):
        buf = ffi.from_buffer(inbuf)
        res = ffi.buffer(buf)
        return res
