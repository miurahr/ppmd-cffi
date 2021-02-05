#from _ppmd import ffi as ffi, lib as lib
from typing import Any, BinaryIO, Optional

READ_BLOCKSIZE: int

def dostime_to_dt(dosdate: Any, dostime: Any): ...
def dt_to_dostime(dt: Any): ...
def datetime_to_timestamp(dt: Any): ...
def dst_write(b: bytes, size: int, userdata: object) -> None: ...
def src_readinto(b: bytes, size: int, userdata: object) -> int: ...

class Ppmd7Encoder:
    closed: bool = ...
    flushed: bool = ...
    destination: Any = ...
    ppmd: Any = ...
    rc: Any = ...
    writer: Any = ...
    def __init__(self, destination: BinaryIO, max_order: int, mem_size: int) -> None: ...
    def encode(self, inbuf: Any) -> None: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, type: Any, value: Any, traceback: Any) -> None: ...

class Ppmd7Decoder:
    ppmd: Any = ...
    rc: Any = ...
    reader: Any = ...
    source: Any = ...
    closed: bool = ...
    def __init__(self, source: BinaryIO, max_order: int, mem_size: int) -> None: ...
    def decode(self, length: Any) -> bytes: ...
    def close(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
PpmdDecoder = Ppmd7Decoder
PpmdEncoder = Ppmd7Encoder

class Ppmd8Decoder:
    closed: bool = ...
    source: Any = ...
    ppmd: Any = ...
    reader: Any = ...
    max_order: Any = ...
    mem_size: Any = ...
    restore: Any = ...
    def __init__(self, source: BinaryIO, max_order: int, mem_size: int, restore: int) -> None: ...
    def decode(self, length: Any): ...
    def close(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

class Ppmd8Encoder:
    closed: bool = ...
    flushed: bool = ...
    destination: Any = ...
    ppmd: Any = ...
    writer: Any = ...
    def __init__(self, destination: BinaryIO, max_order: int, mem_size: int, restore: int) -> None: ...
    def encode(self, inbuf: Any) -> None: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

class PpmdHeader:
    size: int = ...
    time: Any = ...
    attr: int = ...
    info: Any = ...
    fnlen: Any = ...
    restore: Any = ...
    version: Any = ...
    filename: Any = ...
    def __init__(self, *, fname: str = ..., ftime: int = ..., version: int = ..., order: int = ..., mem_in_mb: int = ..., restore: int = ...) -> None: ...
    def read(self, file: Any) -> None: ...
    def write(self, file: Any) -> None: ...
    def __len__(self): ...

class PpmdDecompressor:
    decoder: Any = ...
    file: Any = ...
    filename: Any = ...
    size: Any = ...
    ftime: Any = ...
    def __init__(self, file: Any, filesize: Any) -> None: ...
    def decompress(self, ofile: Any) -> None: ...
    def close(self) -> None: ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
    def __enter__(self): ...

class PpmdCompressor:
    encoder: Any = ...
    def __init__(self, ofile: Any, fname: Any, ftime: Any, order: Any, mem: Any, version: int = ...) -> None: ...
    def compress(self, src: Any) -> None: ...
    def close(self) -> None: ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
    def __enter__(self): ...
Ppmd8Decompressor = PpmdDecompressor
Ppmd8Compressor = PpmdCompressor

def main(arg: Optional[Any]=...) -> Any: ...
