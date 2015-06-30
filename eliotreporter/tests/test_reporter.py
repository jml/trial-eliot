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
from twisted.trial import unittest

from eliot.testing import assertContainsFields, capture_logging, LoggedAction

from eliotreporter import EliotReporter
from .._reporter import TEST


class TestEliotReporter(unittest.TestCase):

    def make_reporter(self, stream=None):
        if stream is None:
            stream = StringIO()
        return EliotReporter(stream, None, None, None)

    def make_test(self):
        return self

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
