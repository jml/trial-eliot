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

from pyrsistent import m, pmap
import unittest2 as unittest


from .._parse import Action, Message, parse_json_stream, to_tasks


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


class TestTasks(unittest.TestCase):

    def test_single_task(self):
        messages = map(
            Message.new, [
                m(task_uuid='foo', task_level=[1]),
                m(task_uuid='foo', task_level=[2]),
            ])
        self.assertEqual(m(foo=messages), to_tasks(messages))

    def test_multiple_tasks(self):
        messages = map(
            Message.new, [
                m(task_uuid='foo', task_level=[1]),
                m(task_uuid='bar', task_level=[1]),
                m(task_uuid='foo', task_level=[2]),
            ])
        self.assertEqual(
            m(
                foo=[messages[0], messages[2]],
                bar=[messages[1]],
            ),
            to_tasks(messages))

    def test_unordered_messages(self):
        messages = map(
            Message.new, [
                m(task_uuid='foo', task_level=[2]),
                m(task_uuid='foo', task_level=[1]),
            ])
        self.assertEqual(m(foo=[messages[1], messages[0]]), to_tasks(messages))

    def test_no_task_uuid(self):
        messages = map(
            Message.new, [
                m(foo="bar"),
            ])
        self.assertEqual(pmap({None: messages}), to_tasks(messages))

    def test_no_task_level(self):
        messages = map(
            Message.new, [
                m(task_uuid='foo'),
                m(task_uuid='foo'),
            ])
        self.assertEqual(m(foo=messages), to_tasks(messages))


class TestActions(unittest.TestCase):

    def test_simple_action_task_uuid(self):
        start_time = time.time()
        end_time = start_time + 10
        messages = [
            Message.new(m(
                task_uuid='foo',
                task_level=[1],
                action_type='omelette',
                timestamp=start_time,
            )),
            Message.new(m(
                task_uuid='foo',
                task_level=[2],
                action_status='succeeded',
                timestamp=end_time,
            )),
        ]
        action = Action.new(messages)
        self.assertEqual('foo', action.task_uuid)
        self.assertEqual('succeeded', action.status)
        self.assertEqual([], action.messages)
        self.assertEqual(datetime.fromtimestamp(start_time), action.start_time)

    def test_multiple_tasks(self):
        messages = [
            Message.new(m(
                task_uuid='foo',
                task_level=[1],
                action_type='omelette',
            )),
            Message.new(m(
                task_uuid='bar',
                task_level=[2],
                action_status='succeeded',
            )),
        ]
        self.assertRaises(ValueError, Action.new, messages)

    # XXX: Incomplete actions
    # - does end_time make sense?

    # XXX: Actions that fail with exceptinons

    # XXX: Actions that have success fields added

    # XXX: Operation on incomplete actions to add a message?

    # XXX: Actions that contain actions

    # XXX: Duration property
