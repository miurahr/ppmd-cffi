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


Command line
============

`ppmd-cffi` provide command line script to hande `.ppmd` file.

To compress file

.. code-block:: bash

    $ ppmd target.dat

To decompress ppmd file

.. code-block:: bash

    $ ppmd -x target.ppmd


To decompress to STDOUT

.. code-block:: bash

    $ ppmd -x -c target.ppmd


Programming Interfaces
======================

`.ppmd` file comression/decompression
=====================================

ppmd-cffi project provide two functions which compress and decompress `.ppmd` archive file.
`PpmdCompressor` class provide compress function `compress()` and `PpmdDecompressor` class
provide extraction function `decompress()`.

Both classes takes `version=` argument which default is 8, means PPMd Ver. I.
Also classes takes `target`, `fname` and `ftime` arguments which is a target file and its properties.
`target` should be a file-like object which has `write()` method.
`fname` and `ftime` is a file property which is stored in archive as meta data.
`fname` should be string, and `ftime` should be a datetime object.

`order` and `mem_in_mb` parameters will be vary.

Compression with PPMd ver. H
----------------------------

.. code-block:: python

    targetfile = pathlib.Path('target.dat')
    fname = 'target.dat'
    ftime = datetime.utcfromtimestamp(targetfile.stat().st_mtime)
    archivefile = 'archive.ppmd'
    order = 6
    mem_in_mb = 16
    with archivefile.open('wb') as target:
        with targetfile.open('rb') as src:
            with PpmdCompressor(target, fname, ftime, order, mem_in_mb, version=7) as compressor:
                compressor.compress(src)


Compression with PPMd ver. I
----------------------------

.. code-block:: python

    targetfile = pathlib.Path('target.dat')
    fname = 'target.dat'
    ftime = datetime.utcfromtimestamp(targetfile.stat().st_mtime)
    archivefile = 'archive.ppmd'
    order = 6
    mem_in_mb = 8
    with archivefile.open('wb') as target:
        with targetfile.open('rb') as src:
            with PpmdCompressor(target, fname, ftime, order, mem_in_mb, version=8) as compressor:
                compressor.compress(src)


Decompression
-------------

When construct `PpmdDecompressor` object, it read header from specified archive file.
The header hold a compression parameters such as PPMd version, order and memory size.
It also has a `filename` and `timestamp`.
`PpmdDecompressor` select a proper decoder based on header data.
You need to handle `filename` and `timestamp` by your self.
A decompressor method will write data to specified file-like object, which should have
`write()` method.

.. code-block:: python

    targetfile = pathlib.Path('target.ppmd')
    with targetfile.open('rb') as target:
        with PpmdDecompressor(target, target_size) as decompressor:
            extractedfile = pathlib.Path(parent.joinpath(decompressor.filename))
            with extractedfile.open('wb') as ofile:
                decompressor.decompress(ofile)
                timestamp = datetime_to_timestamp(decompressor.ftime)
                os.utime(str(extractedfile), times=(timestamp, timestamp))


Bare encoding/decoding PPMd data
================================

There are several classes to handle bare PPMd data. Note: mem parameter should be
as bytes not MB.

* Ppmd7Encoder(dst, order, mem)
* Ppmd7Decoder(src, order, mem)
* Ppmd8Encoder(det, order, mem, restore)
* Ppmd8Decoder(src, order, mem, restore)
