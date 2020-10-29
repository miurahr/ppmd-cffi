import hashlib
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
        with ppmd.Ppmd8Encoder(dst, 6, 8 << 20, 0) as encoder:
            encoder.encode(source)
            encoder.flush()
        dst.seek(0)
        result = dst.getvalue()
    assert result == encoded


def test_ppmd8_decoder():
    with io.BytesIO() as src:
        src.write(encoded)
        src.seek(0)
        with ppmd.Ppmd8Decoder(src, 6, 8 << 20, 0) as decoder:
            result = decoder.decode(len(source))
    assert result == source


def test_ppmd8_encode_decode(tmp_path):
    length = 0
    m = hashlib.sha256()
    with testdata_path.joinpath('10000SalesRecords.csv').open('rb') as f:
        with tmp_path.joinpath('target.ppmd').open('wb') as target:
            with ppmd.Ppmd8Encoder(target, 6, 8 << 20, 0) as enc:
                data = f.read(READ_BLOCKSIZE)
                while len(data) > 0:
                    m.update(data)
                    length += len(data)
                    enc.encode(data)
                    data = f.read(READ_BLOCKSIZE)
                enc.flush()
    shash = m.digest()
    m2 = hashlib.sha256()
    with tmp_path.joinpath('target.ppmd').open('rb') as target:
        with tmp_path.joinpath('target.csv').open('wb') as out:
            with ppmd.Ppmd8Decoder(target, 6, 8 << 20, 0) as dec:
                remaining = length
                while remaining > 0:
                    max_length = min(remaining, READ_BLOCKSIZE)
                    res = dec.decode(max_length)
                    remaining -= len(res)
                    m2.update(res)
                    out.write(res)
                res = dec.decode(remaining)
                remaining -= len(res)
                m2.update(res)
                out.write(res)
    thash = m2.digest()
    assert thash == shash
