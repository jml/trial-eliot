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

from eliot import add_destination
from pyrsistent import PClass, field
from twisted.plugin import IPlugin
from twisted.trial.itrial import IReporter
from zope.interface import implementer

from ._types import (
    ERROR,
    FAILURE,
    SKIP,
    TEST,
    UNEXPECTED_SUCCESS,
    make_error_message,
    make_expected_failure_message,
)


class InvalidStateError(Exception):
    """
    Raised when someone attempts to put an EliotReporter into an invalid state.
    """

# TODO: The Trial base reporter does some sort of warning capturing. It would
# be good to do something similar here so that *everything* that the test
# emits is captured in single, coheerent Eliot log.

# TODO: Ideally we'd also capture stdout & stderr and encode those as Eliot
# messages. Probably can't be done at the reporter level, but we can provide
# functions for tests to be able to use that.

# TODO: Should setUp, tearDown, the test itself and cleanup also be Eliot
# actions? If so, that's a thing for the base test case rather than the
# reporter.

# TODO: Currently Eliot has support for capturing the eliot logs and dumping
# them to the Twisted log, which Trial stores as _trial_temp/test.log. If
# we're using something like this, then we actually want all of those log
# messages to be included as part of the test action, included in the same
# log.

# TODO: "The value is in the output". No one is going to care about this
# unless there's something that consumes the output and displays the results
# as something that matters to humans.

# TODO: Currently the action of a test "succeeds" whether or not the test
# passes. It's unclear whether this is the right behaviour. Factors:
#
# - when reading eliot output, it makes it harder to see whether a test
#   passed or failed.
# - tests can have multiple errors, if we made the action fail on test failure,
#   then we'd have to aggregate these errors somehow.
# - aggregating the errors would mean that we either would not see them at all
#   until the test completes, or that we would log duplicate actions


@implementer(IReporter)
class EliotReporter(object):

    def __init__(self, stream, tbformat='default', realtime=False,
                 publisher=None, logger=None):
        # TODO: Trial has a pretty confusing set of expectations for
        # reporters. In particular, it's not clear what it needs to construct
        # a reporter. It's also not clear what it expects as public
        # properties. The IReporter interface and the tests for the reporter
        # interface cover somewhat different things.
        self._stream = stream
        self.tbformat = tbformat
        self.shouldStop = False
        self.testsRun = 0
        add_destination(self._write_message)
        self._current_test = None
        self._successful = True
        self._logger = logger

    def _write_message(self, message):
        self._stream.write(json.dumps(message) + "\n")

    def _ensure_test_running(self, expected_test):
        current = self._current_test
        if current and current.id() != expected_test.id():
            raise InvalidStateError(
                'Expected {} to be running, was {} instead'.format(
                    expected_test, self._current_test))

    def startTest(self, method):
        """
        Report the beginning of a run of a single test method.

        @param method: an object that is adaptable to ITestMethod
        """
        if self._current_test:
            raise InvalidStateError(
                'Trying to start {}, but {} already started'.format(
                    method, self._current_test))
        self._current_test = method
        self._action = TEST(test=method, logger=self._logger)
        # TODO: This isn't using Eliot the way it was intended. Probably a
        # better way is to have a test case (or a testtools-style TestCase
        # runner!) that does all of this.
        self._action.__enter__()

    def stopTest(self, method):
        """
        Report the status of a single test method

        @param method: an object that is adaptable to ITestMethod
        """
        if not self._current_test:
            raise InvalidStateError(
                'Trying to stop {} without starting it first'.format(method))
        self._ensure_test_running(method)
        self._current_test = None
        self._action.__exit__(None, None, None)

    def addSuccess(self, test):
        """
        Record that test passed.
        """
        self._ensure_test_running(test)

    def addError(self, test, error):
        """
        Record that a test has raised an unexpected exception.
        """
        self._ensure_test_running(test)
        make_error_message(ERROR, error).write(self._logger)
        self._successful = False

    def addFailure(self, test, failure):
        """
        Record that a test has failed with the given failure.
        """
        self._ensure_test_running(test)
        make_error_message(FAILURE, failure).write(self._logger)
        self._successful = False

    def addExpectedFailure(self, test, failure, todo):
        """
        Record that the given test failed, and was expected to do so.
        """
        self._ensure_test_running(test)
        make_expected_failure_message(todo, failure).write(self._logger)

    def addUnexpectedSuccess(self, test, todo):
        """
        Record that the given test failed, and was expected to do so.
        """
        self._ensure_test_running(test)
        UNEXPECTED_SUCCESS(todo=todo).write(self._logger)

    def addSkip(self, test, reason):
        """
        Record that a test has been skipped for the given reason.
        """
        self._ensure_test_running(test)
        SKIP(reason=reason).write(self._logger)

    def wasSuccessful(self):
        return self._successful

    def stop(self):
        self.shouldStop = True

    def done(self):
        """
        Called when the test run is complete.
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
