===============
PPMd for python
===============

.. image:: https://readthedocs.org/projects/ppmd-cffi/badge/?version=latest
  :target: https://ppmd-cffi.readthedocs.io/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/ppmd-cffi.svg
  :target: https://badge.fury.io/py/ppmd-cffi

.. image:: https://github.com/miurahr/ppmd-cffi/workflows/Run%20Tox%20tests/badge.svg
  :target: https://github.com/miurahr/ppmd-cffi/actions

.. image:: https://coveralls.io/repos/github/miurahr/ppmd-cffi/badge.svg?branch=master
  :target: https://coveralls.io/github/miurahr/ppmd-cffi?branch=master




PPM(Prediction by partial matching) is a compression algorithm which has several variations of implementations.
PPMd is the implementation by Dmitry Shkarin. It is used in the RAR by default and by 7-Zip as one of several possible methods.

ppmd, aka. ppmd-cffi, is a python bindings with PPMd implementation by C language.
Core codes are derived from p7zip, portable 7-zip implementation, and now only consist of Ppmd7, PPMd ver.H.

Since 7-zip uses PPMd ver.H and RAR uses PPMd ver.I, the ppmd-cffi is considered compatible with 7-zip's implementation. 

Development status
==================

A development status is condidere as `3 - Alpha`


Installation
============

As usual, you can install ppmd-cffi using python standard pip command.
CAUTION: Since it is a bindings with C source code, C compiler should be installed on your operating system.

```
pip install ppmd-cffi
```

All C source codes are bundled with ppmd-cffi package.

Usage
=====

ppmd-cffi provide two classes. Both class supports context manager, ie. `with ... as ..` syntax.

Encoder
-------

Encoder class provide PPMd encoder. It has `encode()`, `flush()` and `close()` methos.

Decoder
-------

Decoder class pvoride PPMd decoder. It has `decode()` and `close()` methods.

Please see test code for a detailed usage.


License
=======

* Copyright (C) 2020 Hiroshi Miura

* 7-Zip Copyright (C) 1999-2010 Igor Pavlov
* LZMA SDK Copyright (C) 1999-2010 Igor Pavlov

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301  USA
