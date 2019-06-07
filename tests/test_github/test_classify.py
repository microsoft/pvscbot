# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import http
import json

import gidgethub
import gidgethub.sansio
import importlib_resources
import pytest

from . import samples
from pvscbot.github import classify, labels


class FakeGH:
    def __init__(self):
        self.post_ = []
        self.delete_ = []
        self.getiter_request = []
        self.getiter_response = None

    async def getiter(self, url, url_vars={}):
        self.getiter_request.append(gidgethub.sansio.format_url(url, url_vars))
        for x in self.getiter_response:
            yield x

    async def post(self, url, url_vars={}, *, data):
        post_url = gidgethub.sansio.format_url(url, url_vars)
        self.post_.append((post_url, data))

    async def delete(self, url, url_vars={}):
        delete_url = gidgethub.sansio.format_url(url, url_vars)
        self.delete_.append(delete_url)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data_filename",
    [
        "issues-opened.json",
        "issues-reopened-no_labels.json",
        "issues-opened-labels_but_no_status.json",
    ],
)
async def test_issue_with_no_labels(data_filename):
    sample_data = json.loads(importlib_resources.read_text(samples, data_filename))
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="12345")
    gh = FakeGH()
    gh.getiter_response = sample_data["issue"]["labels"]

    await classify.router.dispatch(event, gh)
    assert len(gh.post_) == 1
    action = gh.post_[0]
    assert (
        action[0]
        == f"https://api.github.com/repos/Microsoft/vscode-python/issues/{sample_data['issue']['number']}/labels"
    )
    assert action[1] == {"labels": [labels.Status.classify.value]}


@pytest.mark.asyncio
async def test_new_issue_with_status_label():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-opened_with_labels.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="12345")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert not gh.post_


@pytest.mark.asyncio
async def test_new_issue_gains_status_label_while_processing():
    webhook_data = json.loads(
        importlib_resources.read_text(samples, "issues-opened.json")
    )
    eventual_data = json.loads(
        importlib_resources.read_text(samples, "issues-opened_with_labels.json")
    )
    event = gidgethub.sansio.Event(webhook_data, event="issues", delivery_id="12345")
    gh = FakeGH()
    gh.getiter_response = eventual_data["issue"]["labels"]

    await classify.router.dispatch(event, gh)
    assert not gh.post_


@pytest.mark.asyncio
async def test_new_issue_gains_no_status_label_while_processing():
    webhook_data = json.loads(
        importlib_resources.read_text(samples, "issues-opened.json")
    )
    eventual_data = json.loads(
        importlib_resources.read_text(
            samples, "issues-opened-labels_but_no_status.json"
        )
    )
    event = gidgethub.sansio.Event(webhook_data, event="issues", delivery_id="12345")
    gh = FakeGH()
    gh.getiter_response = eventual_data["issue"]["labels"]

    await classify.router.dispatch(event, gh)
    assert len(gh.post_) == 1
    action = gh.post_[0]
    assert action[1] == {"labels": [labels.Status.classify.value]}


@pytest.mark.asyncio
async def test_adding_classify():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-labeled-classify.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="12345")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert not gh.post_
    assert not gh.delete_


@pytest.mark.asyncio
async def test_removing_classify_label():
    sample_data = json.loads(
        importlib_resources.read_text(
            samples, "issues-labeled-has_classify_adding_triage.json"
        )
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert len(gh.delete_) == 1
    assert (
        gh.delete_[0]
        == "https://api.github.com/repos/Microsoft/vscode-python/issues/3327/labels/classify"
    )


@pytest.mark.asyncio
async def test_removing_classify_label_for_data_science():
    sample_data = json.loads(
        importlib_resources.read_text(
            samples, "issues-labeled-has_classify_adding_data_science.json"
        )
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert len(gh.delete_) == 1
    assert (
        gh.delete_[0]
        == "https://api.github.com/repos/Microsoft/vscode-python/issues/3327/labels/classify"
    )


@pytest.mark.asyncio
async def test_keeping_classify_label():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-labeled-has_classify.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert not gh.delete_


@pytest.mark.asyncio
async def test_removing_missing_classify_label():
    # Can happen if issue is updated since webhook triggered.
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-labeled-has_classify.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")

    class FakeGHDeleteException(FakeGH):
        async def delete(self, url, url_vars={}):
            raise gidgethub.BadRequest(
                http.HTTPStatus.BAD_REQUEST, "Label does not exist"
            )

    gh = FakeGHDeleteException()

    await classify.router.dispatch(event, gh)
    assert not gh.delete_


@pytest.mark.asyncio
async def test_removing_classify_label_error():
    sample_data = json.loads(
        importlib_resources.read_text(
            samples, "issues-labeled-has_classify_adding_triage.json"
        )
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")

    class FakeGHDeleteException(FakeGH):
        async def delete(self, url, url_vars={}):
            raise gidgethub.BadRequest(http.HTTPStatus.BAD_REQUEST, "oops")

    gh = FakeGHDeleteException()

    with pytest.raises(gidgethub.BadRequest):
        await classify.router.dispatch(event, gh)


@pytest.mark.asyncio
async def test_adding_classify_label_again():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-unlabeled-no_labels.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert len(gh.post_) == 1
    assert gh.post_[0] == (
        "https://api.github.com/repos/Microsoft/vscode-python/issues/3327/labels",
        {"labels": [labels.Status.classify.value]},
    )


@pytest.mark.asyncio
async def test_removing_label_no_status_left():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-unlabeled-no_status.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert len(gh.post_) == 1
    assert gh.post_[0] == (
        "https://api.github.com/repos/Microsoft/vscode-python/issues/3327/labels",
        {"labels": [labels.Status.classify.value]},
    )


@pytest.mark.asyncio
async def test_no_adding_label_on_closed_issue():
    sample_data = json.loads(
        importlib_resources.read_text(
            samples, "issues-unlabeled-closed_with_no_labels.json"
        )
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert not gh.post_
    assert not gh.delete_


@pytest.mark.asyncio
async def test_no_adding_label_for_data_science_on_label_removal():
    sample_data = json.loads(
        importlib_resources.read_text(
            samples, "issues-unlabeled-closed_with_no_labels.json"
        )
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="1")
    gh = FakeGH()

    await classify.router.dispatch(event, gh)
    assert not gh.post_
    assert not gh.delete_
