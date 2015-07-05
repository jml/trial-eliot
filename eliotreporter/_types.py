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
Log types for the Eliot reporter.
"""

from eliot import ActionType, Field, MessageType
from twisted.python.failure import Failure


_TEST = Field(u'test', lambda test: test.id(), u'The test')


"""
The action of running a test.
"""
TEST = ActionType(u'trial:test',
                  [_TEST],
                  [],
                  u'A test')


def _exception_name(exception_class):
    return '{}.{}'.format(
        exception_class.__module__, exception_class.__name__)


# TODO: These get re-used in a few different MessageTypes. Is there a way to
# reduce that duplication by representing these as their own type?
_EXCEPTION = Field(
    u'exception', _exception_name, 'An exception raised by a test')
_REASON = Field(u'reason', unicode, 'The reason for the raised exception')
_TRACEBACK = Field(u'traceback', unicode, 'The traceback')


"""
Logged when an error occurs in a test.
"""
ERROR = MessageType(u'trial:test:error', [_EXCEPTION, _REASON, _TRACEBACK])

"""
Logged when an assertion fails in a test.
"""
FAILURE = MessageType(u'trial:test:failure', [_EXCEPTION, _REASON, _TRACEBACK])


_SKIP_REASON = Field(u'reason', unicode, 'Reason for skipping a test')


"""
Logged when a test is skipped.
"""
SKIP = MessageType(u'trial:test:skip', [_SKIP_REASON])


# TODO: Test *all* the serialization
_TODO = Field(u'todo', lambda x: x.reason)

UNEXPECTED_SUCCESS = MessageType(u'trial:test:unexpected-success', [_TODO])
EXPECTED_FAILURE = MessageType(
    u'trial:test:expected-failure', [
        _TODO,
        _EXCEPTION,
        _REASON,
        _TRACEBACK,
    ],
)


def _failure_to_exception_tuple(failure):
    """
    Convert a ``Failure`` to an exception 3-tuple.
    """
    return (
        failure.value.__class__,
        failure.value,
        failure.getBriefTraceback(),
    )


def _adapt_to_exception_tuple(failure):
    """
    Take whatever failure trial can throw at us and return an exception
    3-tuple.
    """
    if isinstance(failure, Failure):
        return _failure_to_exception_tuple(failure)
    return failure


def make_error_message(message_type, failure):
    """
    Create a message for an error or failure in a test.

    :param message_type: A function that returns a ``Message`` and takes an
        ``exception``, a ``reason``, and a ``traceback``.
    :param failure: The failure that occurred. Either a
        ``twisted.python.failure.Failure`` or an exception 3-tuple.

    :return: An Eliot ``Message``.
    """
    exc_type, exc_value, exc_traceback = _adapt_to_exception_tuple(failure)
    return message_type(
        exception=exc_type,
        reason=exc_value,
        traceback=exc_traceback,
    )


def make_expected_failure_message(todo, failure):
    """
    Create a message for an expected failure.

    :param todo: The reason given for expecting the failure.
    :param failure: The failure that occurred. Either a
        ``twisted.python.failure.Failure`` or an exception 3-tuple.

    :return: An Eliot ``Message``.
    """
    exc_type, exc_value, exc_traceback = _adapt_to_exception_tuple(failure)
    return EXPECTED_FAILURE(
        todo=todo,
        exception=exc_type,
        reason=exc_value,
        traceback=exc_traceback,
    )
