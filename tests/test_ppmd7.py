import hashlib
import io
import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
data = b'This file is located in a folder.This file is located in the root.'
READ_BLOCKSIZE = 16384


def test_ppmd_encoder():
    with io.BytesIO() as dst:
        with ppmd.Ppmd7Encoder(dst, 6, 16 << 20) as encoder:
            encoder.encode(data)
            encoder.flush()
        result = dst.getvalue()
        assert len(result) == 41
    with testdata_path.joinpath('ppmd7.dat').open('rb') as f:
        assert result == f.read()


def test_ppmd_encoder2():
    with io.BytesIO() as dst:
        with ppmd.Ppmd7Encoder(dst, 6, 16 << 20) as encoder:
            encoder.encode(data[:33])
            encoder.encode(data[33:])
            encoder.flush()
        result = dst.getvalue()
        assert len(result) == 41
    with testdata_path.joinpath('ppmd7.dat').open('rb') as f:
        assert result == f.read()


def test_ppmd_decoder():
    with testdata_path.joinpath('ppmd7.dat').open('rb') as f:
        with ppmd.Ppmd7Decoder(f, 6, 16 << 20) as decoder:
            result = decoder.decode(33)
            result += decoder.decode(33)
            assert result == data


def test_ppmd_encode_decode(tmp_path):
    length = 0
    m = hashlib.sha256()
    with testdata_path.joinpath('10000SalesRecords.csv').open('rb') as f:
        with tmp_path.joinpath('target.ppmd').open('wb') as target:
            with ppmd.Ppmd7Encoder(target, 6, 16 << 20) as enc:
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
            with ppmd.Ppmd7Decoder(target, 6, 16 << 20) as dec:
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
