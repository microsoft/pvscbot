import json

import gidgethub.sansio
import importlib_resources
import pytest


from ...github import labels, news
from . import samples


class FakeGH:
    def __init__(self):
        self.post_ = []

    async def post(self, url, url_vars={}, *, data):
        post_url = gidgethub.sansio.format_url(url, url_vars)
        self.post_.append((post_url, data))


@pytest.mark.asyncio
async def test_status():
    url = "https://api.github.com/repos/Microsoft/vscode-python/statuses/f1013549456d13eb15dab4fffaa6cfe172b4244e"
    gh = FakeGH()
    event = gidgethub.sansio.Event(
        {"pull_request": {"statuses_url": url}}, event="pull_request", delivery_id="1"
    )
    description = "some description"
    await news.status(event, gh, news.Status.error, description)
    assert len(gh.post_) == 1
    args = gh.post_[0]
    assert len(args) == 2
    assert args[0] == url
    assert args[1] == {
        "state": "error",
        "target_url": "https://github.com/Microsoft/vscode-python/tree/master/news",
        "description": description,
        "context": "pvscbot/news",
    }


@pytest.mark.asyncio
async def test_check_for_skip_news_label(monkeypatch):
    status_args = None

    async def status(*args):
        nonlocal status_args
        status_args = args

    monkeypatch.setattr(news, "status", status)

    data = json.loads(
        importlib_resources.read_text(samples, "pull_request-labeled-skip_news.json")
    )
    event = gidgethub.sansio.Event(data, event="pull_request", delivery_id="1")
    assert await news.check_for_skip_news_label(event, object())
    assert news.Status.success in status_args

    data["pull_request"]["labels"] = []
    status_args = None
    assert not await news.check_for_skip_news_label(event, object())
    assert status_args is None


@pytest.mark.asyncio
async def test_check_for_skip_news_removed(monkeypatch):
    check_args = None

    async def check_for_news_file(*args):
        nonlocal check_args
        check_args = args

    monkeypatch.setattr(news, "check_for_news_file", check_for_news_file)

    data = json.loads(
        importlib_resources.read_text(samples, "pull_request-unlabeled-skip_news.json")
    )
    event = gidgethub.sansio.Event(data, event="pull_request", delivery_id="1")
    await news.check_for_skip_news_label_removed(event, object())
    assert check_args is not None

    check_args = None
    data["label"]["name"] = "something other than 'skip news'"
    await news.check_for_skip_news_label_removed(event, object())
    assert check_args is None


@pytest.mark.asyncio
async def test_check_for_news_file():
    # XXX proper file
    # XXX File in wrong subdirectory
    # XXX File in news/ only
    # XXX Mis-named file
    pass


@pytest.mark.asyncio
async def test_check_for_news():
    # XXX labeled
    # XXX file
    # XXX nothing
    pass


@pytest.mark.asyncio
async def test_routing():
    # XXX label added
    # XXX label removed
    # XXX opened w/ label
    # XXX opened w/ file
    # XXX reopend
    # XXX syncrhonized
    pass
