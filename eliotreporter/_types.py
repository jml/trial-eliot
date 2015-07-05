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


ERROR = MessageType(u'trial:test:error', [_EXCEPTION, _REASON, _TRACEBACK])
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
