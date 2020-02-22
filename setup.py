#!/usr/bin/env python

from setuptools import find_packages
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='refine_label',
    version='1.0.0',
    description='Remove small islands from multiple-valued label',
    long_description=open('README.md').read(),
    author='yuta-hi',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['connected-components-3d'],
    url='https://github.com/yuta-hi/remove-island',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
