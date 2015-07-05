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

"""
Tests for our logging types, focusing on serialization.
"""

import sys

from eliot.testing import assertContainsFields, capture_logging
from twisted.python.failure import Failure
from twisted.trial.unittest import makeTodo
import unittest2 as unittest

from .._types import (
    make_error_message,
    make_expected_failure_message,
    ERROR,
    FAILURE,
    SKIP,
    TEST,
    UNEXPECTED_SUCCESS,
)


def make_exc_tuple(exception):
    try:
        raise exception
    except:
        return sys.exc_info()


def make_failure(exception):
    try:
        raise exception
    except:
        return Failure()


def serialize_message(logger, message):
    message.write()
    [serialized] = logger.serialize()
    return serialized


class TestTypes(unittest.TestCase):

    @capture_logging(None)
    def test_action(self, logger):
        with TEST(test=self):
            pass
        [start, end] = logger.serialize()
        assertContainsFields(self, start, {
            u'action_status': u'started',
            u'action_type': u'trial:test',
            u'test': self.id(),
        })
        assertContainsFields(self, end, {
            u'action_status': u'succeeded',
            u'action_type': u'trial:test',
        })

    @capture_logging(None)
    def test_error(self, logger):
        exception = RuntimeError('All things go')
        exc_tuple = make_exc_tuple(exception)
        message = serialize_message(
            logger, make_error_message(ERROR, exc_tuple))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:error',
            u'reason': 'All things go',
            u'exception': 'exceptions.RuntimeError',
        })

    @capture_logging(None)
    def test_error_from_failure(self, logger):
        exception = RuntimeError('All things go')
        failure = make_failure(exception)
        message = serialize_message(
            logger, make_error_message(ERROR, failure))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:error',
            u'reason': 'All things go',
            u'exception': 'exceptions.RuntimeError',
        })

    @capture_logging(None)
    def test_failure(self, logger):
        exception = AssertionError('All things go')
        exc_tuple = make_exc_tuple(exception)
        message = serialize_message(
            logger, make_error_message(FAILURE, exc_tuple))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:failure',
            u'reason': 'All things go',
            u'exception': 'exceptions.AssertionError',
        })

    @capture_logging(None)
    def test_failure_from_failure(self, logger):
        exception = AssertionError('All things go')
        failure = make_failure(exception)
        message = serialize_message(
            logger, make_error_message(FAILURE, failure))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:failure',
            u'reason': 'All things go',
            u'exception': 'exceptions.AssertionError',
        })

    # TODO: Test skip serialization

    @capture_logging(None)
    def test_skip(self, logger):
        # TODO: Right now, I can't be arsed figuring out what Trial stashes in
        # its skip results, so this is just a first pass attempt.
        message = serialize_message(logger, SKIP(reason='foo'))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:skip',
            u'reason': u'foo',
        })

    @capture_logging(None)
    def test_unexpected_success(self, logger):
        # TODO: Hilariously, `makeTodo` returns `None` when given unicode.
        # File a bug when back online.
        todo = makeTodo('some excuse')
        message = serialize_message(logger, UNEXPECTED_SUCCESS(todo=todo))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:unexpected-success',
            u'todo': u'some excuse',
        })

    @capture_logging(None)
    def test_unexpected_success_specific_exceptions(self, logger):
        todo = makeTodo((RuntimeError, 'some excuse'))
        message = serialize_message(logger, UNEXPECTED_SUCCESS(todo=todo))
        # TODO: We ought to capture and log the expected exceptions rather
        # than silently ignore them.
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:unexpected-success',
            u'todo': u'some excuse',
        })

    @capture_logging(None)
    def test_expected_failure(self, logger):
        todo = makeTodo('some excuse')
        exception = RuntimeError('All things go')
        exc_tuple = make_exc_tuple(exception)
        message = serialize_message(
            logger, make_expected_failure_message(todo, exc_tuple))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:expected-failure',
            u'todo': u'some excuse',
            u'exception': u'exceptions.RuntimeError',
            u'reason': u'All things go',
        })

    @capture_logging(None)
    def test_expected_failure_specific_exceptions(self, logger):
        todo = makeTodo((RuntimeError, 'some excuse'))
        exception = RuntimeError('All things go')
        exc_tuple = make_exc_tuple(exception)
        message = serialize_message(
            logger, make_expected_failure_message(todo, exc_tuple))
        assertContainsFields(self, message, {
            u'message_type': u'trial:test:expected-failure',
            u'todo': u'some excuse',
            u'exception': u'exceptions.RuntimeError',
            u'reason': u'All things go',
        })
