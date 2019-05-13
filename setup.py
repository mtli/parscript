"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup
# codes.open is for support of python 2.x
from codecs import open
from os import path

import re

here = path.abspath(path.dirname(__file__))
re_ver = re.compile(r"__version__\s+=\s+'(.*)'")
with open(path.join(here, 'parscript', '__init__.py'), encoding='utf-8') as f:
    version = re_ver.search(f.read()).group(1)

setup(
    name='parscript',
    version=version,
    description='Parallel or distributed execution of jobs',
    long_description='See project page: https://github.com/mtli/parscript',
    url='https://github.com/mtli/parscript',
    author='Mengtian (Martin) Li',
    author_email='martinli.work@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: System :: Distributed Computing',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
    ],
    keywords='parallel computing distributed computing',
    packages=['parscript'],
    install_requires=[
        'portalocker',
    ],
    include_package_data = True,
)
