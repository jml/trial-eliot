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


from .._parse import (
    Action,
    AmbiguousMessageKind,
    Message,
    MessageKind,
    parse_json_stream,
    to_tasks,
)


def make_uuid():
    return object()


def make_message_data(**kwargs):
    return m(**kwargs)


def make_timestamp():
    return time.time()


class TestParser(unittest.TestCase):

    def test_json_stream(self):
        data = '{"foo": "bar"}\n{"baz": "qux"}'
        expected = [m(foo="bar"), m(baz="qux")]
        self.assertEqual(expected, list(parse_json_stream(data.splitlines())))


class TestMessage(unittest.TestCase):

    def test_task_uuid(self):
        task_uuid = make_uuid()
        data = make_message_data(task_uuid=task_uuid)
        message = Message.new(data)
        self.assertEqual(task_uuid, message.task_uuid)

    def test_task_level(self):
        task_level = [1]
        data = make_message_data(task_level=[1])
        message = Message.new(data)
        self.assertEqual(task_level, message.task_level)

    def test_timestamp(self):
        timestamp = make_timestamp()
        data = make_message_data(timestamp=timestamp)
        message = Message.new(data)
        self.assertEqual(datetime.fromtimestamp(timestamp), message.timestamp)

    def test_other_fields(self):
        data = make_message_data(foo="bar", baz="qux")
        message = Message.new(data)
        self.assertEqual(m(foo="bar", baz="qux"), message.fields)

    def test_message_type(self):
        data = make_message_data(foo="bar", baz="qux", message_type="test:type")
        message = Message.new(data)
        self.assertEqual('test:type', message.entry_type)

    def test_as_dict(self):
        task_uuid = make_uuid()
        task_level = [1]
        timestamp = make_timestamp()
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


class TestMessageKind(unittest.TestCase):

    def test_message_kind(self):
        data = make_message_data(foo="bar", baz="qux")
        message = Message.new(data)
        self.assertEqual(MessageKind.MESSAGE, message.kind)

    def test_action_start_kind(self):
        data = make_message_data(
            foo="bar", baz="qux", action_type="test:type",
            action_status="started")
        message = Message.new(data)
        self.assertEqual(MessageKind.ACTION_START, message.kind)

    def test_action_success_kind(self):
        data = make_message_data(
            foo="bar", baz="qux", action_type="test:type",
            action_status="succeeded")
        message = Message.new(data)
        self.assertEqual(MessageKind.ACTION_END, message.kind)

    def test_action_failure_kind(self):
        data = make_message_data(
            foo="bar", baz="qux", action_type="test:type",
            action_status="failed")
        message = Message.new(data)
        self.assertEqual(MessageKind.ACTION_END, message.kind)

    def test_action_type_without_status(self):
        data = make_message_data(
            foo="bar", baz="qux", action_type="test:type")
        self.assertRaises(AmbiguousMessageKind, Message.new, data)

    def test_action_type_and_message_type(self):
        data = make_message_data(
            foo="bar", baz="qux", action_type="test:type",
            message_type="different:type", action_status="started")
        self.assertRaises(AmbiguousMessageKind, Message.new, data)


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
                action_status='started',
                timestamp=start_time,
            )),
            Message.new(m(
                task_uuid='foo',
                task_level=[2],
                action_type='omelette',
                action_status='succeeded',
                timestamp=end_time,
            )),
        ]
        action = Action.new(messages)
        self.assertEqual('foo', action.task_uuid)
        self.assertEqual('succeeded', action.status)
        self.assertEqual([], action.messages)
        self.assertEqual(datetime.fromtimestamp(start_time), action.start_time)
        self.assertEqual(datetime.fromtimestamp(end_time), action.end_time)

    def test_multiple_tasks(self):
        messages = [
            Message.new(m(
                task_uuid='foo',
                task_level=[1],
                action_type='omelette',
                action_status='started',
            )),
            Message.new(m(
                task_uuid='bar',
                task_level=[2],
                action_type='omelette',
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
