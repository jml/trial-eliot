#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="trial-eliot",
    version="0.1.0",
    description="Eliot reporter for Trial.",
    author="Jonathan Lange",
    author_email="jml@mumak.net",
    install_requires=[],
    zip_safe=False,
    packages=find_packages('.'),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ],
)
