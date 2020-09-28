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
The library has a bere function and no metadata/header handling functions.
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

    data = b'abcdefghijk'
    level = 6
    memSize = 16  # 16Mb
    with ppmd.PpmdBufferEncoder(level, memSize) as encoder:
        result = encoder.encode(data)
        result += encoder.flush()


There is also `ppmd.PpmdEncoder(f: BinaryIO, level, memSize)` interface.

Decompression/Decoding
----------------------

.. code-block:: python

    level = 6
    memSize = 16
    with pathlib.Path('compressed.data.bin').open('rb') as f:
        with ppmd.PpmdDecoder(f, level, memSize) as decoder:
            result = decoder.decode(outsize1)
            result += decoder.decode(outsize2)
        assert len(result) == outsize1 + outsizse2

There is also `ppmd.PpmdBufferDecoder(level, memSize)` interface, which
decode ONE-SHOT data, as like `result = decoder.decode(data, outsize)`
