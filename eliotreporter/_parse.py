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
Take the output of an Eliot reporter and turn it into something useful.
"""

from datetime import datetime
from itertools import imap
import json
from operator import attrgetter

from pyrsistent import PClass, field, freeze, ny, pvector, v
from toolz.itertoolz import groupby
from twisted.python.constants import Names, NamedConstant


# TODO: No doubt much of this is more general than eliotreporter, or tests.
# Share it in a better way.

# TODO: Also, this duplicates logic from eliottree (but implemented in a
# different way). Can we reduce the duplication somehow?

# PLAN:
# - stream of JSON to stream of dictionaries
# - dictionaries to Messages (task_uuid, timestamp, task_level, ???, fields)
# - stream of Messages to Tasks and ungrouped Messages
# - each Task to tree of actions
# - find actions that are tests (action_type == 'trial:test')
# - interpret those actions as tests

# XXX: Not clear on which exceptions are likely to be seen by users (most
# likely due to corrupt data) and which exceptions "cannot happen" but are
# worth having anyway for fast failure in the case of assumption failure.


# XXX: These should really be defined by eliot itself.
STARTED = 'started'
SUCCEEDED = 'succeeded'
FAILED = 'failed'

ALL_STATUSES = (STARTED, SUCCEEDED, FAILED)
TERMINAL_STATUSES = (SUCCEEDED, FAILED)


def fmap(f, x):
    return None if x is None else f(x)


def remove_fields(d, fields):
    e = d.evolver()
    for f in fields:
        if f in e:
            del e[f]
    return e.persistent()


def get_timestamp(contents):
    return fmap(datetime.fromtimestamp, contents.get('timestamp'))


class AmbiguousMessageKind(Exception):

    # XXX: Move this to be closer to the other exceptions

    def __init__(self, message, reason):
        super(AmbiguousMessageKind, self).__init__(
            'Could not determine MessageKind for {}: {}'.format(
                message, reason))


class MessageKind(Names):
    """
    Different kinds of messages.

    All Eliot log entries are either Messages, the start of an Action, or the
    end of an Action.
    """

    MESSAGE = NamedConstant()
    ACTION_START = NamedConstant()
    ACTION_END = NamedConstant()


def _get_message_kind(message_data):
    """
    Given a dict of message data, return its kind and type.
    """
    if 'action_type' in message_data:
        if 'message_type' in message_data:
            raise AmbiguousMessageKind(
                message_data, 'action_type and message_type both present')
        action_status = message_data.get('action_status')
        action_type = message_data.get('action_type')
        if action_status == 'started':
            return MessageKind.ACTION_START, action_type
        elif action_status in ('succeeded', 'failed'):
            return MessageKind.ACTION_END, action_type
        else:
            raise AmbiguousMessageKind(
                message_data,
                'Unrecognized action_status: {}'.format(action_status))
    else:
        return MessageKind.MESSAGE, message_data.get('message_type')


class Message(PClass):
    """
    A parsed Eliot message.
    """

    task_uuid = field()
    task_level = field()
    timestamp = field()
    fields = field()
    entry_type = field()
    # XXX: Can we restrict the type of thhis?
    kind = field()

    @classmethod
    def new(klass, contents):
        kind, entry_type = _get_message_kind(contents)
        # XXX: Can probably reduce the duplication here and represent these as
        # data.
        fields = remove_fields(
            contents, [
                'task_uuid',
                'task_level',
                'timestamp',
                'message_type',
                'action_type',
            ])
        return klass(
            task_uuid=contents.get('task_uuid'),
            task_level=contents.get('task_level'),
            timestamp=get_timestamp(contents),
            entry_type=entry_type,
            kind=kind,
            fields=fields,
        )

    def as_dict(self):
        fields = self.fields.evolver()
        fields['task_uuid'] = self.task_uuid
        fields['task_level'] = self.task_level
        # XXX: Not quite a full reversal, because the Python APIs for turning
        # datetimes into Unix timestamps are awful and jml is too tired and
        # lazy to bother right now.
        fields['timestamp'] = self.timestamp
        return fields.persistent()


def _to_tasks(messages):
    return freeze(groupby(attrgetter('task_uuid'), messages))


def _sort_by_level(messages):
    return pvector(sorted(messages, key=attrgetter('task_level')))


def to_tasks(messages):
    """Group a sequence of ``Message`` objects by task.

    A "task" is a top-level action identified by a ``task_uuid`` field. All
    messages that have the same value of ``task_uuid`` are part of the same
    task.

    Returns a dictionary mapping ``task_uuid`` to a sequence of messages
    sorted by task level.
    """
    tasks = _to_tasks(messages)
    return tasks.transform([ny], _sort_by_level)


def _finished(message):
    return (v(), message)


def _in_progress(stack):
    return (stack, None)


def _pop(stack):
    return (stack[:-1], stack[-1])


def _push(stack, x):
    return (stack.append(x), None)


def _append_to_top(stack, message):
    new_stack, top_action = _pop(stack)
    return _push(new_stack, top_action._append_message(message))


def _receive_message(action_stack, message):
    kind = message.kind

    if kind == MessageKind.ACTION_START:
        return _push(action_stack, Action._start(message))

    elif kind == MessageKind.MESSAGE:
        if not action_stack:
            return _finished(message)
        else:
            return _append_to_top(action_stack, message)

    elif kind == MessageKind.ACTION_END:
        if not action_stack:
            raise EndWithoutStart(message)

        (new_stack, current_action) = _pop(action_stack)
        finished_action = current_action._append_message(message)

        if new_stack:
            return _append_to_top(new_stack, finished_action)
        else:
            return _finished(finished_action)

    else:
        raise AssertionError(
            'Unknown kind for message {}: {}'.format(message, kind))


def _collapse_stack(stack):
    if not stack:
        raise AssertionError('Can only collapse non-empty stacks')
    if len(stack) == 1:
        return stack[0]
    return stack[0]._append_message(_collapse_stack(stack[1:]))


def make_nested_actions(messages):
    # XXX: This smells like a fold function to me.
    stack = v()
    for message in messages:
        (new_stack, result) = _receive_message(stack, message)
        # XXX: Can we do this without assignment?
        stack = new_stack
        if new_stack and result:
            raise AssertionError(
                'Received {} while we still had unprocessed input: {}'.format(
                    result, stack))
        elif new_stack:
            continue
        elif result:
            yield result
        else:
            raise AssertionError(
                'Tried to process {} but got no result'.format(message))
    if stack:
        # XXX: Alternatively, we might want to raise an exception here.
        yield _collapse_stack(stack)


def _get_task_uuid(messages):
    """
    Return the single task_uuid of messages.

    If there is more than one task_uuid, raise DifferentTasks.

    If there are no task_uuids, return None.
    """
    task_uuids = frozenset(x.task_uuid for x in messages)
    try:
        [task_uuid] = list(task_uuids)
    except ValueError:
        raise DifferentTasks(messages)
    return task_uuid


class DifferentTasks(Exception):
    """Messages ought to be in the same task, but aren't."""

    def __init__(self, messages):
        super(DifferentTasks, self).__init__(
            'Expected {} to be in the same task'.format(messages))


class AlreadyEnded(Exception):
    """Tried to end an action that's already ended."""

    def __init__(self, action, message):
        super(AlreadyEnded, self).__init__(
            'Tried to end {} with {}, but it was already ended.'.format(
                action, message))


class IncompatibleEnd(Exception):
    """
    Tried to end an action with a different type to the one that started it.
    """

    def __init__(self, action, message):
        super(IncompatibleEnd, self).__init__(
            'Tried to end {} with {}, but types are incompatible '
            '({} != {}).'.format(
                action, message, action.entry_type, message.entry_type))


class NotStarted(Exception):
    """Tried to create an action without a start message."""

    def __init__(self, message):
        super(NotStarted, self).__init__(
            'Tried to start with non-start message: {}'.format(message))


class AlreadyStarted(Exception):
    """Tried to append a start action to an action."""

    def __init__(self, action, message):
        super(AlreadyStarted, self).__init__(
            'Tried to append {} to already-started {}.'.format(
                message, action))


class EndWithoutStart(Exception):
    """Tried to end an action when there was none started."""

    # XXX: Is this really different from NotStarted?

    def __init__(self, message):
        super(EndWithoutStart, self).__init__(
            'Got end message {} when there was nothing on the stack'.format(
                message))


class Action(PClass):
    """
    An Eliot Action.
    """

    messages = field()

    entry_type = field()
    task_uuid = field()
    start_time = field()
    end_time = field()
    status = field()

    @classmethod
    def new(cls, messages):
        # XXX: Probably shouldn't bother providing this "simple" interface for
        # actions. Instead, will provide a function that does the full, nested
        # monty.

        # XXX: Hey, look! It's another fold.

        # XXX: Doesn't allow receiving messages out-of-order. Maybe we should
        # sort first? Or allow out-of-order in _append? At the least, document
        # it.

        # XXX: No way to retrieve original messages.
        action = cls._start(messages[0])
        if len(messages) == 1:
            return action
        for message in messages[1:]:
            action = action._append_message(message)
        return action

    @classmethod
    def _start(cls, message):
        # XXX: whither message.fields?
        status = message.fields.get('action_status')
        if status != STARTED:
            raise NotStarted(message)
        return cls(
            messages=pvector(),
            task_uuid=message.task_uuid,
            start_time=message.timestamp,
            end_time=None,
            entry_type=message.entry_type,
            status=status,
        )

    def _append_message(self, message):
        _get_task_uuid([self, message])
        if self._is_ended():
            raise AlreadyEnded(self, message)

        fields = getattr(message, 'fields', None)
        if not fields:
            # Then it's probably an action.
            return self.set(messages=self.messages.append(message))

        status = fields.get('action_status')
        if not status:
            # Then it's just a normal message.
            return self.set(messages=self.messages.append(message))

        if status == STARTED:
            # Nested actions are handled elsewhere.
            raise AlreadyStarted(self, message)

        if status in TERMINAL_STATUSES:
            # XXX: whither message.fields?
            if message.entry_type != self.entry_type:
                raise IncompatibleEnd(self, message)
            return self.set(
                end_time=message.timestamp,
                status=status,
            )

        # XXX: Probably have dedicated exception.
        raise ValueError('Unknown status: {}'.format(status))

    def _is_ended(self):
        # XXX: add invariant for end_time & status being terminal
        return self.end_time or self.status in TERMINAL_STATUSES


def _parse_entry(entry):
    """Parse a single serialized JSON object."""
    return freeze(json.loads(entry))


def parse_json_stream(lines):
    """
    Parse a stream of JSON objects.

    Assumes that ``lines`` is an iterable of serialized JSON objects.
    """
    for line in lines:
        try:
            yield _parse_entry(line.strip())
        except ValueError as e:
            # Silently ignore non-JSON lines.
            # XXX: make this behaviour hookable
            pass


def parse_to_tasks(lines):
    # XXX: Untested
    messages = imap(Message.new, parse_json_stream(lines))
    tasks = to_tasks(messages)
    # XXX: Undefined behaviour for messages that aren't in a task (i.e. the
    # contents of tasks[None])
    for task in tasks.itervalues():
        for action in make_nested_actions(task):
            yield action
