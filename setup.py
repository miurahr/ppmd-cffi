from setuptools import setup

setup(use_scm_version={"local_scheme": "no-local-version"},
      package_dir={"": "src"},
      cffi_modules=["src/ffi_build.py:ffibuilder"])
