import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
orders = [3, 4, 4, 5, 5, 6, 8, 16, 24, 32]


def test_encoder_constructor():
    encoder = ppmd.Encoder(6)


def test_decoder():
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        # props = b'\x06\x00\x00\x01\x00'
        with ppmd.Decoder(f, 6, 16) as decoder:
            result = decoder.decode(41)
        assert result is not None
        assert len(result) == 41
