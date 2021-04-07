import pathlib
import shutil
import sys
import tempfile

from hypothesis import given
from hypothesis import strategies as st

import ppmd

MAX_SIZE = min(0xFFFFFFFF - 12 * 3, sys.maxsize)


@given(obj=st.binary(min_size=1),
       max_order=st.integers(min_value=2, max_value=64),
       mem_size=st.integers(min_value=1 << 11, max_value=MAX_SIZE))
def test_ppmd7_fuzzer(obj, max_order, mem_size):
    tmp_path = pathlib.Path(tempfile.mkdtemp())
    with tmp_path.joinpath('target.ppmd').open('wb') as target:
        with ppmd.Ppmd7Encoder(target, max_order=max_order, mem_size=mem_size) as enc:
            enc.encode(obj)
            enc.flush()
    with tmp_path.joinpath('target.ppmd').open('rb') as target:
        with ppmd.Ppmd7Decoder(target, max_order=max_order, mem_size=mem_size) as dec:
            res = dec.decode(len(obj))
    assert obj == res
    shutil.rmtree(tmp_path)


if __name__ == "__main__":
    import atheris  # type: ignore  # noqa

    atheris.Setup(sys.argv, test_ppmd7_fuzzer.hypothesis.fuzz_one_input)
    atheris.Fuzz()
