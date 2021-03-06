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
import json
from operator import attrgetter

from pyrsistent import PClass, field, freeze, ny, pvector
from toolz.itertoolz import groupby


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


class Message(PClass):
    """
    A parsed Eliot message.
    """

    task_uuid = field()
    task_level = field()
    timestamp = field()
    fields = field()

    @classmethod
    def new(klass, contents):
        fields = remove_fields(
            contents, [
                'task_uuid',
                'task_level',
                'timestamp',
            ])
        return klass(
            task_uuid=contents.get('task_uuid'),
            task_level=contents.get('task_level'),
            timestamp=get_timestamp(contents),
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


class Action(PClass):
    """
    An Eliot Action.
    """

    end_time = field()
    messages = field()
    start_time = field()
    status = field()
    task_uuid = field()

    @classmethod
    def new(cls, messages):
        [task_uuid] = list(set(m.task_uuid for m in messages))
        # XXX: Add another layer so we have ActionStart, ActionSuccess, and
        # ActionFailed "messages". Then the responsibility of this class is
        # merely to assemble those into a coherent representation of an
        # Action, raising errors for type validation.
        status = messages[-1].fields.get('action_status')
        return cls(
            messages=pvector(),
            status=status,
            task_uuid=task_uuid,
            start_time=messages[0].timestamp,
            end_time=messages[-1].timestamp,
        )


def _parse_entry(entry):
    """Parse a single serialized JSON object."""
    return freeze(json.loads(entry))


def parse_json_stream(lines):
    """
    Parse a stream of JSON objects.

    Assumes that ``lines`` is an iterable of serialized JSON objects.
    """
    for line in lines:
        yield _parse_entry(line.strip())




def main():
    from pprint import pprint
    from pyrsistent import thaw
    import sys
    with open(sys.argv[1]) as f:
        tasks = to_tasks(Message.new(x) for x in parse_json_stream(f))
        pprint(thaw(tasks))
