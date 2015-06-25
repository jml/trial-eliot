
Trial reporter for [Eliot](http://eliot.rtfd.org).

Currently a prototype.

## Example

```
$ trial --reporter=eliot twisted.trial.test.test_reporter
{"task_uuid": "0335b448-7689-4f9a-a94b-7795194c89ff", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AdaptedReporterTests.test_addError", "timestamp": 1435250867.777076, "action_status": "started"}
{"timestamp": 1435250867.777433, "task_uuid": "0335b448-7689-4f9a-a94b-7795194c89ff", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "b68fb0f8-381d-4a1c-a62e-0f17d3f75d27", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AdaptedReporterTests.test_addExpectedFailure", "timestamp": 1435250867.777572, "action_status": "started"}
{"timestamp": 1435250867.777796, "task_uuid": "b68fb0f8-381d-4a1c-a62e-0f17d3f75d27", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "f26be45e-4204-409c-b3d1-e6759dae0bd4", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AdaptedReporterTests.test_addFailure", "timestamp": 1435250867.777931, "action_status": "started"}
{"timestamp": 1435250867.778146, "task_uuid": "f26be45e-4204-409c-b3d1-e6759dae0bd4", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "07b26bbd-29ab-4ad2-a992-e6787bcc4121", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AdaptedReporterTests.test_addSkip", "timestamp": 1435250867.778281, "action_status": "started"}
{"timestamp": 1435250867.778495, "task_uuid": "07b26bbd-29ab-4ad2-a992-e6787bcc4121", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "32fdff2b-0201-4a00-86c6-684d546e685d", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AdaptedReporterTests.test_addUnexpectedSuccess", "timestamp": 1435250867.778626, "action_status": "started"}
{"timestamp": 1435250867.778805, "task_uuid": "32fdff2b-0201-4a00-86c6-684d546e685d", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "dac22d76-1892-4be8-9caa-505debabc92e", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AdaptedReporterTests.test_startTest", "timestamp": 1435250867.778941, "action_status": "started"}
{"timestamp": 1435250867.779114, "task_uuid": "dac22d76-1892-4be8-9caa-505debabc92e", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "ceeaf7b7-d519-468b-9fea-b0b10fc873b5", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AdaptedReporterTests.test_stopTest", "timestamp": 1435250867.779242, "action_status": "started"}
{"timestamp": 1435250867.779418, "task_uuid": "ceeaf7b7-d519-468b-9fea-b0b10fc873b5", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "6d115645-68f0-441f-9ff5-c7273e06027b", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AnsiColorizerTests.test_supportedNoCurses", "timestamp": 1435250867.779548, "action_status": "started"}
{"timestamp": 1435250867.779834, "task_uuid": "6d115645-68f0-441f-9ff5-c7273e06027b", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "24a16156-ade8-4855-a4db-5c4d2c66a896", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AnsiColorizerTests.test_supportedSetupTerm", "timestamp": 1435250867.779973, "action_status": "started"}
{"timestamp": 1435250867.780215, "task_uuid": "24a16156-ade8-4855-a4db-5c4d2c66a896", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "ed15545b-96b1-4f6a-9a36-904920cfd70e", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AnsiColorizerTests.test_supportedStdOutTTY", "timestamp": 1435250867.780352, "action_status": "started"}
{"timestamp": 1435250867.780544, "task_uuid": "ed15545b-96b1-4f6a-9a36-904920cfd70e", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "ccff7d63-96e3-4923-a34b-8e40f67b5828", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AnsiColorizerTests.test_supportedTigetNumErrors", "timestamp": 1435250867.78069, "action_status": "started"}
{"timestamp": 1435250867.780927, "task_uuid": "ccff7d63-96e3-4923-a34b-8e40f67b5828", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "b56d3c8d-2472-48d9-98e1-6bdedcf03338", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AnsiColorizerTests.test_supportedTigetNumNotEnoughColor", "timestamp": 1435250867.781065, "action_status": "started"}
{"timestamp": 1435250867.781294, "task_uuid": "b56d3c8d-2472-48d9-98e1-6bdedcf03338", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "2a1f382b-c994-4f2c-8be8-bc1985304aaa", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.AnsiColorizerTests.test_supportedTigetNumWrongError", "timestamp": 1435250867.781447, "action_status": "started"}
{"timestamp": 1435250867.781705, "task_uuid": "2a1f382b-c994-4f2c-8be8-bc1985304aaa", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
{"task_uuid": "9dd357e9-ae3d-44ee-9588-bae4f30d87e6", "task_level": [1], "action_type": "trial:test", "test": "twisted.trial.test.test_reporter.DirtyReactorTests.test_dealsWithThreeTuples", "timestamp": 1435250867.781843, "action_status": "started"}
{"timestamp": 1435250867.782075, "task_uuid": "9dd357e9-ae3d-44ee-9588-bae4f30d87e6", "action_type": "trial:test", "action_status": "succeeded", "task_level": [2]}
...
```

### eliot-tree

```
$ trial --reporter=eliot twisted.trial.test.test_reporter | eliot-tree
485eb03f-9177-497a-933d-c0ae00719942
    +-- trial:test@1/started
        |-- test: twisted.trial.test.test_reporter.AdaptedReporterTests.test_addError
        `-- timestamp: 2015-06-25 17:49:01.658038
    +-- trial:test@2/succeeded
        `-- timestamp: 2015-06-25 17:49:01.658390

ffe6f93a-ac1d-4ebc-9835-ecc16722f183
    +-- trial:test@1/started
        |-- test: twisted.trial.test.test_reporter.AdaptedReporterTests.test_addExpectedFailure
        `-- timestamp: 2015-06-25 17:49:01.658533
    +-- trial:test@2/succeeded
        `-- timestamp: 2015-06-25 17:49:01.658754

e5cb7de8-1d94-4cb1-9c97-1b1a9266fd53
    +-- trial:test@1/started
        |-- test: twisted.trial.test.test_reporter.AdaptedReporterTests.test_addFailure
        `-- timestamp: 2015-06-25 17:49:01.658885
    +-- trial:test@2/succeeded
        `-- timestamp: 2015-06-25 17:49:01.659101

0eab6b9c-4f0a-4e38-b32a-755d795e896a
    +-- trial:test@1/started
        |-- test: twisted.trial.test.test_reporter.AdaptedReporterTests.test_addSkip
        `-- timestamp: 2015-06-25 17:49:01.659233
    +-- trial:test@2/succeeded
        `-- timestamp: 2015-06-25 17:49:01.659445

```
