import io
import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
data = b'This file is located in a folder.This file is located in the root.'


def test_encoder(tmp_path):
    with tmp_path.joinpath('target.dat').open('wb') as t:
        with ppmd.Encoder(t, 6, 16) as encoder:
            encoder.encode(data)


def test_decoder():
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        with ppmd.Decoder(f, 6, 16) as decoder:
            result = decoder.decode(66)
        assert result is not None
        assert len(result) == 66
        assert result == data
