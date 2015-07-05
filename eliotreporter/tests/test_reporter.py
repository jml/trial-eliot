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

from StringIO import StringIO
import unittest2 as unittest

from eliot import Field, MessageType
from eliot.testing import assertContainsFields, capture_logging, LoggedAction

from eliotreporter import EliotReporter
from .._reporter import TEST


DUMMY_MESSAGE = MessageType(
    u'test_reporter:dummy', [Field('foo', str)], u'Dummy message for testing')


def get_task_ids(messages):
    return set((x['task_uuid'] for x in messages))


class ExampleTests(unittest.TestCase):
    """
    Tests used to exercise the reporter.
    """

    def __init__(self, method_name, exception=None):
        super(ExampleTests, self).__init__(method_name)
        self._exception = exception

    def success(self):
        pass

    def log_message(self):
        DUMMY_MESSAGE(foo='bar').write()

    def failure(self):
        if self._exception:
            raise self._exception
        else:
            self.fail('Failing with no specified exception')


class TestEliotReporter(unittest.TestCase):

    def make_reporter(self, stream=None):
        if stream is None:
            stream = StringIO()
        return EliotReporter(stream, None, None, None)

    def make_test(self):
        return ExampleTests('success')

    def make_logging_test(self):
        return ExampleTests('log_message')

    def make_failing_test(self, ignored):
        return ExampleTests('failure', ignored)

    def assert_one_task(self, messages):
        self.assertEqual(1, len(get_task_ids(messages)), messages)

    @capture_logging(None)
    def test_successful_test(self, logger):
        """
        Starting and stopping a test logs a whole action.
        """
        reporter = self.make_reporter()
        test = self.make_test()
        reporter.startTest(test)
        reporter.stopTest(test)
        [action] = LoggedAction.of_type(logger.serialize(), TEST)
        assertContainsFields(self, action.start_message, {"test": test.id()})

    @capture_logging(None)
    def test_run_successful_test(self, logger):
        """
        Running a test with the Eliot reporter logs an action.
        """
        reporter = self.make_reporter()
        test = self.make_test()
        test.run(reporter)
        [action] = LoggedAction.of_type(logger.serialize(), TEST)
        assertContainsFields(self, action.start_message, {"test": test.id()})

    @capture_logging(None)
    def test_message_within_test(self, logger):
        """
        A message logged within a test is logged inside the containing action.
        """
        reporter = self.make_reporter()
        test = self.make_logging_test()
        test.run(reporter)
        self.assertEqual(
            [[1], [2], [3]],
            [x['task_level'] for x in logger.messages])
        self.assert_one_task(logger.messages)

    @capture_logging(None)
    def test_run_failing_test(self, logger):
        """
        Running a failing test records the failure as a message.
        """
        reporter = self.make_reporter()
        error = AssertionError('1 != 3')
        test = self.make_failing_test(error)
        test.run(reporter)
        self.assert_one_task(logger.messages)
        failure_message = dict(logger.messages[1])
        failure_message.pop('task_uuid')
        failure_message.pop('timestamp')
        failure_message.pop('traceback')
        self.assertEqual(
            {u'exception': error.__class__,
             u'message_type': u'trial:test:failure',
             u'reason': error,
             u'task_level': [2],
            }, failure_message)
