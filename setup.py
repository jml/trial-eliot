#!/usr/bin/env python
#
# Copyright (c) 2015 Jonathan M. Lange <jml@mumak.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


setup(
    name="trial-eliot",
    version="0.1.0",
    description="Eliot reporter for Trial.",
    author="Jonathan Lange",
    author_email="jml@mumak.net",
    install_requires=[
        'eliot',
        'pyrsistent',
        'toolz',
        'Twisted',
        'zope.interface',
    ],
    tests_require=[
        'unittest2',
    ],
    entry_points={
        'console_scripts': [
            'trial-eliot-parse = eliotreporter._parse:main',
        ],
    },
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
