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
from twisted.trial.test import test_reporter
from twisted.trial.unittest import makeTodo, SkipTest, SynchronousTestCase

from eliotreporter import EliotReporter
from .._reporter import TEST, InvalidStateError


DUMMY_MESSAGE = MessageType(
    u'test_reporter:dummy', [Field('foo', str)], u'Dummy message for testing')


def get_task_ids(messages):
    return set((x['task_uuid'] for x in messages))


def make_reporter(stream=None):
    if stream is None:
        stream = StringIO()
    return EliotReporter(stream, None, None, None)


def make_test(function, *args, **kwargs):
    """
    Make a test that just runs the function with the given arguments.
    """
    class ExampleTest(SynchronousTestCase):
        def __init__(self, method_name, function, args, kwargs):
            super(ExampleTest, self).__init__(method_name)
            self._function = function
            self._args = args
            self._kwargs = kwargs

        def run_function(self):
            function = self._function
            args = self._args
            kwargs = self._kwargs
            function(self, *args, **kwargs)

    return ExampleTest('run_function', function, args, kwargs)


def make_successful_test():
    return make_test(lambda *args: None)


def _raise(exception):
    raise exception


def make_failing_test(reason):
    return make_test(lambda test: test.fail(reason))


def make_erroring_test(exception):
    return make_test(lambda ignored: _raise(exception))


def make_skipping_test(reason):
    error = SkipTest(reason)
    return make_erroring_test(error)


def make_expected_failure_test(reason, function, *args, **kwargs):
    test = make_test(function, *args, **kwargs)
    test.todo = reason
    return test


class TestEliotReporter(unittest.TestCase):

    def assert_one_task(self, messages):
        self.assertEqual(1, len(get_task_ids(messages)), messages)

    @capture_logging(None)
    def test_successful_test(self, logger):
        """
        Starting and stopping a test logs a whole action.
        """
        reporter = make_reporter()
        test = make_successful_test()
        reporter.startTest(test)
        reporter.stopTest(test)
        [action] = LoggedAction.of_type(logger.serialize(), TEST)
        assertContainsFields(self, action.start_message, {"test": test.id()})

    @capture_logging(None)
    def test_run_successful_test(self, logger):
        """
        Running a test with the Eliot reporter logs an action.
        """
        reporter = make_reporter()
        test = make_successful_test()
        test.run(reporter)
        [action] = LoggedAction.of_type(logger.serialize(), TEST)
        assertContainsFields(self, action.start_message, {"test": test.id()})

    @capture_logging(None)
    def test_message_within_test(self, logger):
        """
        A message logged within a test is logged inside the containing action.
        """
        reporter = make_reporter()
        message = DUMMY_MESSAGE(foo='bar')
        test = make_test(lambda ignored: message.write())
        test.run(reporter)
        # TODO: We can probably assert more specific things, that `message` is
        # one of the logged `messages`.
        self.assertEqual(
            [[1], [2], [3]],
            [x['task_level'] for x in logger.messages])
        self.assert_one_task(logger.messages)

    @capture_logging(None)
    def test_run_failing_test(self, logger):
        """
        Running a failing test records the failure as a message.
        """
        reporter = make_reporter()
        reason = '1 != 3'
        test = make_failing_test(reason)
        test.run(reporter)
        self.assert_one_task(logger.messages)
        failure_message = dict(logger.messages[1])
        failure_message.pop('task_uuid')
        failure_message.pop('timestamp')
        failure_message.pop('traceback')
        observed_reason = failure_message.pop('reason')
        self.assertEqual(reason, unicode(observed_reason))
        self.assertEqual(
            {u'exception': test.failureException,
             u'message_type': u'trial:test:failure',
             u'task_level': [2],
            }, failure_message)

    @capture_logging(None)
    def test_run_erroring_test(self, logger):
        """
        Running a test that raises an error records the error as a message.
        """
        reporter = make_reporter()
        error = RuntimeError('everything is catching on fire')
        test = make_erroring_test(error)
        test.run(reporter)
        self.assert_one_task(logger.messages)
        failure_message = dict(logger.messages[1])
        failure_message.pop('task_uuid')
        failure_message.pop('timestamp')
        failure_message.pop('traceback')
        self.assertEqual(
            {u'exception': error.__class__,
             u'message_type': u'trial:test:error',
             u'reason': error,
             u'task_level': [2],
            }, failure_message)

    @capture_logging(None)
    def test_run_skipping_test(self, logger):
        """
        Running a test that skips itself records the skip as a message.
        """
        reporter = make_reporter()
        reason = 'No need'
        test = make_skipping_test(reason)
        test.run(reporter)
        self.assert_one_task(logger.messages)
        failure_message = dict(logger.messages[1])
        failure_message.pop('task_uuid')
        failure_message.pop('timestamp')
        self.assertEqual(
            {u'message_type': u'trial:test:skip',
             u'reason': reason,
             u'task_level': [2],
            }, failure_message)

    @capture_logging(None)
    def test_unexpected_success(self, logger):
        """
        Running a test that unexpectedly succeeds logs that success as a
        message.
        """
        reporter = make_reporter()
        reason = 'No need'
        test = make_expected_failure_test(reason, lambda ignored: None)
        test.run(reporter)
        self.assert_one_task(logger.messages)
        failure_message = dict(logger.messages[1])
        failure_message.pop('task_uuid')
        failure_message.pop('timestamp')
        # Because 'Todo' is not a value.
        todo = failure_message.pop('todo')
        self.assertEqual(reason, todo.reason)
        self.assertEqual(
            {u'message_type': u'trial:test:unexpected-success',
             u'task_level': [2],
            }, failure_message)


class TestEliotReporterDefences(unittest.TestCase):
    """Test the defensive assertions in EliotReporter.

    The reporter interface doesn't define what happens when someone tries to
    stop a test that hasn't started, or start a test while another is running.
    It assumes that only one test is running at a time.

    These tests exercise that undefined behaviour. Specifically, the make sure
    that the defensive assertions we've written work as expected.
    """

    def test_start_test_twice(self):
        reporter = make_reporter()
        test = make_successful_test()
        reporter.startTest(test)
        self.assertRaises(InvalidStateError, reporter.startTest, test)

    def test_stop_without_start(self):
        reporter = make_reporter()
        test = make_successful_test()
        self.assertRaises(InvalidStateError, reporter.stopTest, test)

    def test_stop_different_to_start(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        reporter.startTest(test1)
        self.assertRaises(InvalidStateError, reporter.stopTest, test2)

    def test_stop_resets(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        reporter.startTest(test1)
        reporter.stopTest(test1)
        self.assertIs(None, reporter.startTest(test2))

    def test_different_success(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        reporter.startTest(test1)
        self.assertRaises(InvalidStateError, reporter.addSuccess, test2)

    def test_different_failure(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        dummy_failure = (None, None, None)
        reporter.startTest(test1)
        self.assertRaises(
            InvalidStateError, reporter.addFailure, test2, dummy_failure)

    def test_different_error(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        dummy_error = (None, None, None)
        reporter.startTest(test1)
        self.assertRaises(
            InvalidStateError, reporter.addError, test2, dummy_error)

    def test_different_expected_failure(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        dummy_error = (None, None, None)
        dummy_todo = None
        reporter.startTest(test1)
        self.assertRaises(
            InvalidStateError,
            reporter.addExpectedFailure, test2, dummy_error, dummy_todo)

    def test_different_unexpected_success(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        dummy_todo = None
        reporter.startTest(test1)
        self.assertRaises(
            InvalidStateError,
            reporter.addUnexpectedSuccess, test2, dummy_todo)

    def test_different_skip(self):
        reporter = make_reporter()
        test1 = make_successful_test()
        test2 = make_successful_test()
        dummy_reason = None
        reporter.startTest(test1)
        self.assertRaises(
            InvalidStateError, reporter.addSkip, test2, dummy_reason)


class InterfaceTests(test_reporter.ReporterInterfaceTests):

    resultFactory = EliotReporter
