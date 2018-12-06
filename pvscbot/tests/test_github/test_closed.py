import json

import gidgethub.sansio
import importlib_resources
import pytest

from . import samples
from ...github import closed


class FakeGH:
    def __init__(self):
        self.called = []

    async def delete(self, url, url_vars):
        url = gidgethub.sansio.format_url(url, url_vars)
        self.called.append(url)


@pytest.mark.asyncio
async def test_status_label_removal():
    sample_data = json.loads(
        importlib_resources.read_text(samples, "issues-closed.json")
    )
    event = gidgethub.sansio.Event(sample_data, event="issues", delivery_id="12345")
    gh = FakeGH()

    await closed.remove_status_labels(event, gh)
    assert len(gh.called) == 1
    assert gh.called[0] == gidgethub.sansio.format_url(
        "https://api.github.com/repos/Microsoft/vscode-python/issues/3453/labels{/name}",
        {"name": "needs spec"},
    )


# XXX Test routing; @pytest.mark.parametrize('action', ['opened', 'reopened', 'synchronize'])
