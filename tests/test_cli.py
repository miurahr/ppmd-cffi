import os
import shutil

import pytest  # type: ignore

from ppmd import main

testdata_path = os.path.join(os.path.dirname(__file__), 'data')
source = b'This file is located in a folder.This file is located in the root.\n'


def test_cli_help(capsys):
    expected = '''usage: ppmd [-h] [-x] [-c] [-7] target

ppmd

positional arguments:
  target

optional arguments:
  -h, --help   show this help message and exit
  -x           Specify decompression
  -c           Output to stdout
  -7, --seven  Compress with PPMd ver.H instead of Ver.I
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


def test_cli_extract_stdout(capsysbinary, tmp_path):
    arcfile = os.path.join(testdata_path, "data.ppmd")
    shutil.copy(arcfile, tmp_path.joinpath('data.ppmd'))
    target = str(tmp_path.joinpath('data.ppmd'))
    main(["-x", "-c", target])
    captured = capsysbinary.readouterr()
    assert captured.out == source


def test_cli_compress(tmp_path):
    arcfile = os.path.join(testdata_path, "10000SalesRecords.csv")
    shutil.copy(arcfile, tmp_path.joinpath('10000SalesRecords.csv'))
    target = str(tmp_path.joinpath('10000SalesRecords.csv'))
    main([target])


def test_cli_compress7(tmp_path):
    arcfile = os.path.join(testdata_path, "10000SalesRecords.csv")
    shutil.copy(arcfile, tmp_path.joinpath('10000SalesRecords.csv'))
    target = str(tmp_path.joinpath('10000SalesRecords.csv'))
    main(["-7", target])
