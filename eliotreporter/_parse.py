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

import json

from pyrsistent import freeze


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

def _parse_entry(entry):
    return freeze(json.loads(entry))


def parse_json_stream(lines):
    for line in lines:
        yield _parse_entry(line.strip())
