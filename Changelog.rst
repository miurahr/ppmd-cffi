===============
Py7zr ChangeLog
===============

All notable changes to this project will be documented in this file.

`Unreleased`_
=============

Added
-----

Changed
-------

Fixed
-----

Deprecated
----------

Removed
-------

Security
--------

`v0.5.0`_
=========

* Change github repository name from ppmd to ppmd-cffi

Added
-----
* Add CodeQL static code analysis
* Add dependabot dependency checker

Changed
-------
* Set configurations on pyproject.toml(#14)
* README: change status to maintance

`v0.4.2`_
=========

Changed
-------
* Improve performance by moving main loop part into C code.


`v0.4.1`_
=========

Added
-----

* Win32 build

Changed
-------

* Overwhole extension C code headers(#12)
* Update release github actions script to use cibuildwheel action

Fixed
-----

* check mem_size argument with sys.maxsize to avoid overflow (#12)


`v0.4.0`_
=========

Added
-----

* Test case to check range of max_order and mem_size

Changed
-------

* Allocate internal buffer memory with Python's memory manager.

Removed
-------

* Stop publish of AArch64 anylinux package


`v0.3.3`_
=========

* Change to beta status
* Measure test coverage
* Add type hint stubs


`v0.3.2`_
=========

* CLI: handle filename and timestamp properly.


`v0.3.1`_
=========

* Rename to Ppmd7Encoder/Ppmd7Decoder from PpmdEncoder/PpmdDecoder for ver.H.


`v0.3.0`_
=========

* Support PPMd ver.I (PPMd8) encoding.
* Add CLI command ppmd that compress and decompress file using PPMd ver.I
  It is intend to be compatible with ppmd-mini project.
* Drop `*Buffered*` api

`v0.2.5`_
=========

* Publish aarch64 manylinux2014 binary package.

`v0.2.4`_
=========

* Support python 3.9

`v0.2.3`_
=========

* Fix decompression algorithm.
* Release win/mac binaries.

`v0.2.2`_
=========

* Release manylinux binary on PyPI.
* Fix CI/CD configuration for main branch.

`v0.2.0`_
=========

Changed
-------

* Change mem parameter in MB to mem_size in bytes.
* Change default branch name to main.

`v0.1.0`_
=========

Added
-----

* Add documennts.

Changed
-------

* API change
    - Base API: PpmdEncoder PpmdDecoder class
    - Simple API: PpmdBufferEncoder, PpmdBufferDecoder class

v0.0.5
======

* Change decode API to IOBase.readinto(b)

v0.0.4
======

* Change directory structure.

v0.0.3
======

* Change API to buffer protocol.

v0.0.2
======

* Release automation and support manylinux binary.

v0.0.1
======

* First release.


.. History links
.. _Unreleased: https://github.com/miurahr/py7zr/compare/v0.5.0...HEAD
.. _v0.5.0: https://github.com/miurahr/py7zr/compare/v0.4.1...v0.5.0
.. _v0.4.2: https://github.com/miurahr/py7zr/compare/v0.4.1...v0.4.2
.. _v0.4.1: https://github.com/miurahr/py7zr/compare/v0.4.0...v0.4.1
.. _v0.4.0: https://github.com/miurahr/py7zr/compare/v0.3.3...v0.4.0
.. _v0.3.3: https://github.com/miurahr/py7zr/compare/v0.3.2...v0.3.3
.. _v0.3.2: https://github.com/miurahr/py7zr/compare/v0.3.1...v0.3.2
.. _v0.3.1: https://github.com/miurahr/py7zr/compare/v0.3.0...v0.3.1
.. _v0.3.0: https://github.com/miurahr/py7zr/compare/v0.2.5...v0.3.0
.. _v0.2.5: https://github.com/miurahr/py7zr/compare/v0.2.4...v0.2.5
.. _v0.2.4: https://github.com/miurahr/py7zr/compare/v0.2.3...v0.2.4
.. _v0.2.3: https://github.com/miurahr/py7zr/compare/v0.2.2...v0.2.3
.. _v0.2.2: https://github.com/miurahr/py7zr/compare/v0.2.0...v0.2.2
.. _v0.2.0: https://github.com/miurahr/py7zr/compare/v0.1.0...v0.2.0
.. _v0.1.0: https://github.com/miurahr/py7zr/compare/v0.0.1...v0.1.0
