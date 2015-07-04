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


class ExampleTests(unittest.TestCase):
    """
    Tests used to exercise the reporter.
    """

    def success(self):
        pass

    def log_message(self):
        DUMMY_MESSAGE(foo='bar').write()


class TestEliotReporter(unittest.TestCase):

    def make_reporter(self, stream=None):
        if stream is None:
            stream = StringIO()
        return EliotReporter(stream, None, None, None)

    def make_test(self):
        return ExampleTests('success')

    def make_logging_test(self):
        return ExampleTests('log_message')

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
        Starting and stopping a test logs a whole action.
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
        self.assertEqual(
            1, len(set((x['task_uuid'] for x in logger.messages))))
