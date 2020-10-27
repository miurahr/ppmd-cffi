.. _user_guide:

**********
User Guide
**********

PPM, Prediction by partial matching, is a wellknown compression technique
based on context modeling and prediction. PPM models use a set of previous
symbols in the uncompressed symbol stream to predict the next symbol in the
stream.

PPMd is an implementation of PPMII by Dmitry Shkarin.

The ppmd-cffi package uses core C files from p7zip.
The library has a bare function and no metadata/header handling functions.
This means you should know compression parameters and input/output data
sizes.


Getting started
===============

Install
-------

The ppmd-cffi is written by Python and C language bound with CFFI, and can be downloaded
from PyPI(aka. Python Package Index) using standard 'pip' command as like follows;

.. code-block:: bash

    $ pip install ppmd-cffi


Programming Interfaces
======================

Compression/Encoding
--------------------

.. code-block:: python

    data1 = b'abcdefghijk123456789'
    data2 = b'123456'
    level = 6
    memSize = 16 << 20 # 16Mb
    with pathlib.Path('compressed.data.bin').open('wb') as f:
    with io.BytesIO() as fio:
        with ppmd.PpmdEncoder(fio, level, memSize) as encoder:
            encoder.encode(data1)
            encoder.encode(data2)
            encoder.flush()
    result = fio.getValue()


Decompression/Decoding
----------------------

.. code-block:: python

    level = 6
    memSize = 16
    outsize1 = 16384
    outsize2 = 1245
    with pathlib.Path('compressed.data.bin').open('rb') as infile:
        with ppmd.PpmdDecoder(infile, level, memSize) as decoder:
            result = decoder.decode(outsize1)
            result += decoder.decode(outsize2)
    assert len(result) == outsize1 + outsizse2
