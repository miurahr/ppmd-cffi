import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
orders = [3, 4, 4, 5, 5, 6, 8, 16, 24, 32]


def test_encoder(tmp_path):
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        with tmp_path.joinpath('target.dat').open('wb') as t:
            encoder = ppmd.Encoder(t, 6, 16)
            # encoder.encode(f.read())
            encoder.close()


def test_decoder():
    with testdata_path.joinpath('ppmd.dat').open('rb') as f:
        decoder = ppmd.Decoder(f, 6, 16)
        result = decoder.decode(41)
        #assert result is not None
        #assert len(result) == 41
        decoder.close()
