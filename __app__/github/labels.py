# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import enum


@enum.unique
class Status(enum.Enum):
    classify = "classify"
    triage = "triage"
    needs_decision = "needs decision"
    needs_PR = "needs PR"
    needs_spec = "needs spec"
    needs_upstream_fix = "needs upstream fix"
    experimenting = "experimenting"


STATUS_LABELS = frozenset(e.value for e in Status.__members__.values())


@enum.unique
class Classification(enum.Enum):
    epic = "Epic"
    meta = "meta"
    release_plan = "release plan"


CLASSIFICATION_LABELS = frozenset(e.value for e in Classification.__members__.values())


@enum.unique
class Skip(enum.Enum):
    news = "skip news"


@enum.unique
class Team(enum.Enum):
    data_science = "data science"
    xteam = "xteam"
