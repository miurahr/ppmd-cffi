===============
PPMd for python
===============

.. image:: https://readthedocs.org/projects/ppmd-cffi/badge/?version=latest
  :target: https://ppmd-cffi.readthedocs.io/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/ppmd-cffi.svg
  :target: https://badge.fury.io/py/ppmd-cffi

.. image:: https://github.com/miurahr/ppmd/workflows/Run%20Tox%20tests/badge.svg
  :target: https://github.com/miurahr/ppmd/actions

.. image:: https://coveralls.io/repos/github/miurahr/ppmd/badge.svg?branch=main
  :target: https://coveralls.io/github/miurahr/ppmd?branch=main



Notice
======

A project PPMd(ppmd-cffi) now stopped development.
You are recommended to use PyPPMd_ that is a successor project.

.. _PyPPMd: https://pypi.org/project/pyppmd/

PPM(Prediction by partial matching) is a compression algorithm which has several variations of implementations.
PPMd is the implementation by Dmitry Shkarin. It is used in the RAR and by 7-Zip as one of several possible methods.

ppmd, aka. ppmd-cffi, is a python bindings with PPMd implementation by C language.
The C codes are derived from p7zip, portable 7-zip implementation.
ppmd-cffi support PPMd ver.H and PPMd ver.I.

Manuals
=======

You can find a manual at the readthedocs_

.. _readthedocs: https://ppmd-cffi.readthedocs.io/en/latest/user_guide.html


Installation
============

As usual, you can install ppmd-cffi using python standard pip command.

.. code-block::

    pip install ppmd-cffi


Command
=======

ppmd-cffi provide small utility compress/decompress files.

.. code-block::

    $ ppmd target.txt
    $ ppmd -x target.txt.ppmd


License
=======

* Copyright (C) 2020,2021 Hiroshi Miura

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
