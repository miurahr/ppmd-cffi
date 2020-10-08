import io
import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
data = b'This file is located in a folder.This file is located in the root.'


def test_ppmd_encoder():
    with io.BytesIO() as dst:
        with ppmd.PpmdEncoder(dst, 6, 16 << 20) as encoder:
            encoder.encode(data)
            encoder.flush()
        result = dst.getvalue()
        assert len(result) == 41
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        assert result == f.read()


def test_ppmd_encoder2():
    with io.BytesIO() as dst:
        with ppmd.PpmdEncoder(dst, 6, 16 << 20) as encoder:
            encoder.encode(data[:33])
            encoder.encode(data[33:])
            encoder.flush()
        result = dst.getvalue()
        assert len(result) == 41
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        assert result == f.read()


def test_ppmd_buffer_encoder():
    with ppmd.PpmdBufferEncoder(6, 16 << 20) as encoder:
        result = encoder.encode(data[:33])
        result += encoder.encode(data[33:])
        result += encoder.flush()
        assert len(result) == 41
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        assert result == f.read()


def test_ppmd_decoder():
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        with ppmd.PpmdDecoder(f, 6, 16 << 20) as decoder:
            result = decoder.decode(33)
            result += decoder.decode(33)
            assert result == data


def test_ppmd_buffer_decoder():
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        with ppmd.PpmdBufferDecoder(6, 16 << 20) as decoder:
            result = decoder.decode(f.read(), 66)
    assert result == data
