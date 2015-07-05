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

import json

from eliot import ActionType, add_destination, Field, MessageType
from pyrsistent import PClass, field
from twisted.plugin import IPlugin
from twisted.python.failure import Failure
from twisted.trial.itrial import IReporter
from zope.interface import implementer


_TEST = Field(u'test', lambda test: test.id(), u'The test')


TEST = ActionType(u'trial:test',
                  [_TEST],
                  [],
                  u'A test')


def _exception_name(exception_class):
    return '{}.{}'.format(
        exception_class.__module__, exception_class.__name__)


_EXCEPTION = Field(
    u'exception', _exception_name, 'An exception raised by a test')
_REASON = Field(u'reason', unicode, 'The reason for the raised exception')
_TRACEBACK = Field(u'traceback', unicode, 'The traceback')


FAILURE = MessageType(u'trial:test:failure', [_EXCEPTION, _REASON, _TRACEBACK])


def _failure_to_exception_tuple(failure):
    return (
        failure.value.__class__,
        failure.value,
        failure.getBriefTraceback(),
    )


def _adapt_to_exception_tuple(failure):
    if isinstance(failure, Failure):
        return _failure_to_exception_tuple(failure)
    return failure


def make_error_message(message_type, failure):
    exc_type, exc_value, exc_traceback = _adapt_to_exception_tuple(failure)
    return message_type(
        exception=exc_type,
        reason=exc_value,
        traceback=exc_traceback,
    )


@implementer(IReporter)
class EliotReporter(object):

    def __init__(self, stream, tbformat, rterrors, log):
        self._stream = stream
        self.tbformat = tbformat
        self.args = ()
        self.shouldStop = False
        self.testsRun = 0
        add_destination(self._write_message)

    def _write_message(self, message):
        self._stream.write(json.dumps(message) + "\n")

    def startTest(self, method):
        """
        Report the beginning of a run of a single test method.

        @param method: an object that is adaptable to ITestMethod
        """
        self._action = TEST(test=method)
        self._action.__enter__()

    def stopTest(self, method):
        """
        Report the status of a single test method

        @param method: an object that is adaptable to ITestMethod
        """
        self._action.__exit__(None, None, None)

    def addSuccess(self, test):
        """
        Record that test passed.
        """

    def addError(self, test, error):
        """
        Record that a test has raised an unexpected exception.

        @param test: The test that has raised an error.
        @param error: The error that the test raised. It will either be a
            three-tuple in the style of C{sys.exc_info()} or a
            L{Failure<twisted.python.failure.Failure>} object.
        """

    def addFailure(self, test, failure):
        """
        Record that a test has failed with the given failure.

        @param test: The test that has failed.
        @param failure: The failure that the test failed with. It will
            either be a three-tuple in the style of C{sys.exc_info()}
            or a L{Failure<twisted.python.failure.Failure>} object.
        """
        make_error_message(FAILURE, failure).write()

    def addExpectedFailure(self, test, failure, todo):
        """
        Record that the given test failed, and was expected to do so.

        @type test: L{pyunit.TestCase}
        @param test: The test which this is about.
        @type error: L{failure.Failure}
        @param error: The error which this test failed with.
        @type todo: L{unittest.Todo}
        @param todo: The reason for the test's TODO status.
        """

    def addUnexpectedSuccess(self, test, todo):
        """
        Record that the given test failed, and was expected to do so.

        @type test: L{pyunit.TestCase}
        @param test: The test which this is about.
        @type todo: L{unittest.Todo}
        @param todo: The reason for the test's TODO status.
        """

    def addSkip(self, test, reason):
        """
        Record that a test has been skipped for the given reason.

        @param test: The test that has been skipped.
        @param reason: An object that the test case has specified as the reason
            for skipping the test.
        """

    def wasSuccessful(self):
        """
        Return a boolean indicating whether all test results that were reported
        to this reporter were successful or not.
        """

    def done(self):
        """
        Called when the test run is complete.

        This gives the result object an opportunity to display a summary of
        information to the user. Once you have called C{done} on an
        L{IReporter} object, you should assume that the L{IReporter} object is
        no longer usable.
        """


@implementer(IReporter, IPlugin)
class TrialReporter(PClass):

    name = field()
    module = field()
    description = field()
    longOpt = field()
    shortOpt = field()
    klass = field()


eliot_plugin = TrialReporter(
    name="Eliot reporter",
    description="Output all test results as eliot logs",
    longOpt="eliot",
    shortOpt=None,
    module="eliotreporter",
    klass="EliotReporter",
)
