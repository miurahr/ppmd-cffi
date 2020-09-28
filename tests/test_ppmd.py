import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
data = b'This file is located in a folder.This file is located in the root.'


def test_encoder():
    with ppmd.PpmdEncoder(6, 16) as encoder:
        result = encoder.encode(data)
        result += encoder.flush()
    assert len(result) == 41
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        assert result == f.read()


def test_encoder2():
    with ppmd.PpmdEncoder(6, 16) as encoder:
        result = encoder.encode(data[:33])
        result += encoder.encode(data[33:])
        result += encoder.flush()
    assert len(result) == 41
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        assert result == f.read()


def test_decoder():
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        with ppmd.PpmdDecoder(f, 6, 16) as decoder:
            result = decoder.decode(66)
            assert result == data
