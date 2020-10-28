import binascii
import hashlib
import os
import shutil

import pytest

from ppmd import main

testdata_path = os.path.join(os.path.dirname(__file__), 'data')
source = b'This file is located in a folder.This file is located in the root.\n'

def test_cli_help(capsys):
    expected = '''usage: ppmd [-h] [-x] target

ppmd

positional arguments:
  target

optional arguments:
  -h, --help  show this help message and exit
  -x
'''
    with pytest.raises(SystemExit):
        main(["-h"])
    out, err = capsys.readouterr()
    assert out.startswith(expected)


def test_cli_extract(tmp_path):
    arcfile = os.path.join(testdata_path, "data.ppmd")
    shutil.copy(arcfile, tmp_path.joinpath('data.ppmd'))
    target = str(tmp_path.joinpath('data.ppmd'))
    extracted = tmp_path.joinpath('data')
    main(["-x", target])
    #
    result = extracted.open('rb').read()
    assert result == source
