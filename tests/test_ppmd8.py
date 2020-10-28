import io
import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
source = b'This file is located in a folder.This file is located in the root.\n'
encoded = b'\x54\x16\x43\x6d\x5c\xd8\xd7\x3a\xb3\x58\x31\xac\x1d\x09\x23\xfd\x11\xd5\x72\x62\x73' \
          b'\x13\xb6\xce\xb2\xe7\x6a\xb9\xf6\xe8\x66\xf5\x08\xc3\x0a\x09\x36\x12\xeb\xda\xda\xba'
READ_BLOCKSIZE = 16384


def test_ppmd8_encoder():
    with io.BytesIO() as dst:
        with ppmd.Ppmd8Encoder(dst, 6, 8, 0) as encoder:
            encoder.encode(source)
            encoder.flush()
        dst.seek(0)
        result = dst.getvalue()
    assert result == encoded


def test_ppmd8_decoder():
    with io.BytesIO() as src:
        src.write(encoded)
        src.seek(0)
        with ppmd.Ppmd8Decoder(src, 6, 8, 0) as decoder:
            result = decoder.decode(len(source))
    assert result == source
