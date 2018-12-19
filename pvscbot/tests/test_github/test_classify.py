import json

import gidgethub.sansio
import importlib_resources
import pytest

from . import samples
from ...github import classify, labels


class FakeGH:
    def __init__(self):
        self.post_ = []
        self.delete_ = []

    async def post(self, url, url_vars={}, *, data):
        post_url = gidgethub.sansio.format_url(url, url_vars)
        self.post_.append((post_url, data))

    async def delete(self, url, url_vars={}):
        delete_url = gidgethub.sansio.format_url(url, url_vars)
        self.delete_.append(delete_url)


@pytest.mark.asyncio
async def test_new_issue_with_no_labels():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-opened.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="12345")
    gh = FakeGH()

    await classify.classify_new_issue(event, gh)
    assert len(gh.post_) == 1
    action = gh.post_[0]
    assert (
        action[0]
        == "https://api.github.com/repos/Microsoft/vscode-python/issues/3451/labels"
    )
    assert action[1] == {"labels": [labels.Status.classify.value]}


@pytest.mark.asyncio
async def test_new_issue_with_labels():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-opened_with_labels.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="12345")
    gh = FakeGH()

    await classify.classify_new_issue(event, gh)
    assert not len(gh.post_)


@pytest.mark.asyncio
async def test_removing_classify_label():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-labeled-has_classify.json")
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


# XXX Test routing; @pytest.mark.parametrize('action', ['opened', 'reopened', 'synchronize'])
