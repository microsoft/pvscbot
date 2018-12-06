import json

import gidgethub.sansio
import importlib_resources
import pytest

from . import samples
from ...github import classify, labels


class FakeGH:
    def __init__(self):
        self.post_ = []

    async def post(self, url, url_vars={}, *, data):
        post_url = gidgethub.sansio.format_url(url, url_vars)
        self.post_.append((post_url, data))


@pytest.mark.asyncio
async def test_new_issue_with_no_labels():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-opened.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="12345")
    gh = FakeGH()

    await classify.add_classify_label(event, gh)
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

    await classify.add_classify_label(event, gh)
    assert not len(gh.post_)


# XXX Test routing; @pytest.mark.parametrize('action', ['opened', 'reopened', 'synchronize'])
