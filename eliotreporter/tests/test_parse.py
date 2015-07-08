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

from pyrsistent import m
import unittest2 as unittest


from .._parse import parse_json_stream


class TestParser(unittest.TestCase):

    def test_json_stream(self):
        data = '{"foo": "bar"}\n{"baz": "qux"}'
        expected = [m(foo="bar"), m(baz="qux")]
        self.assertEqual(expected, list(parse_json_stream(data.splitlines())))
