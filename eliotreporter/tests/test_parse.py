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

from datetime import datetime
import time

from pyrsistent import m
import unittest2 as unittest


from .._parse import Message, parse_json_stream


class TestParser(unittest.TestCase):

    def test_json_stream(self):
        data = '{"foo": "bar"}\n{"baz": "qux"}'
        expected = [m(foo="bar"), m(baz="qux")]
        self.assertEqual(expected, list(parse_json_stream(data.splitlines())))


class TestMessage(unittest.TestCase):

    def make_uuid(self):
        return object()

    def make_message_data(self, **args):
        return m(**args)

    def make_timestamp(self):
        return time.time()

    def test_task_uuid(self):
        task_uuid = self.make_uuid()
        data = self.make_message_data(task_uuid=task_uuid)
        message = Message.new(data)
        self.assertEqual(task_uuid, message.task_uuid)

    def test_task_level(self):
        task_level = [1]
        data = self.make_message_data(task_level=[1])
        message = Message.new(data)
        self.assertEqual(task_level, message.task_level)

    def test_timestamp(self):
        timestamp = self.make_timestamp()
        data = self.make_message_data(timestamp=timestamp)
        message = Message.new(data)
        self.assertEqual(datetime.fromtimestamp(timestamp), message.timestamp)

    def test_other_fields(self):
        data = self.make_message_data(foo="bar", baz="qux")
        message = Message.new(data)
        self.assertEqual(m(foo="bar", baz="qux"), message.fields)

    def test_as_dict(self):
        task_uuid = self.make_uuid()
        task_level = [1]
        timestamp = self.make_timestamp()
        data = m(
            task_uuid=task_uuid,
            task_level=task_level,
            timestamp=timestamp,
            foo="bar",
            baz="qux",
        )
        message = Message.new(data)
        self.assertEqual(
            m(
                task_uuid=task_uuid,
                task_level=task_level,
                timestamp=datetime.fromtimestamp(timestamp),
                foo="bar",
                baz="qux",
            ),
            message.as_dict(),
        )
