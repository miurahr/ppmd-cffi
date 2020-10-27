import io
import os
import pathlib

import ppmd

testdata_path = pathlib.Path(os.path.dirname(__file__)).joinpath('data')
data = b'This file is located in a folder.This file is located in the root.'
READ_BLOCKSIZE = 16384


def test_ppmd8_encoder():
    with io.BytesIO() as dst:
        with ppmd.Ppmd8Encoder(dst, 6, 8, 0) as encoder:
            encoder.encode(data)
            encoder.flush()
        result = dst.getvalue()
    assert result == b'\xe0\x00\x00\x00T\x16Cm\\\xd8\xd7:\xb3X1\xac\x1d\t#\xfd\x11' \
                     b'\xd5rbs\x13\xb6\xce\xb2\xe7j\xb9\xf6\xe8f\xf5\x08\xc3\n\t7>\xd2\xa3\x00'


def test_ppmd8_decoder():
    with io.BytesIO() as src:
        src.write(b'\xe0\x00\x00\x00T\x16Cm\\\xd8\xd7:\xb3X1\xac\x1d\t#\xfd\x11' \
                  b'\xd5rbs\x13\xb6\xce\xb2\xe7j\xb9\xf6\xe8f\xf5\x08\xc3\n\t7>\xd2\xa3\x00')
        src.seek(0)
        with ppmd.Ppmd8Decoder(src, 6, 8, 0) as decoder:
            result = decoder.decode(len(data))
    assert result == data
