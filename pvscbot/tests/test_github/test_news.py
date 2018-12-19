import json

import gidgethub.sansio
import importlib_resources
import pytest


from ...github import labels, news
from . import samples


class FakeGH:
    def __init__(self, *, getiter_=[]):
        self.post_ = []
        self.getiter_ = getiter_

    async def post(self, url, url_vars={}, *, data):
        post_url = gidgethub.sansio.format_url(url, url_vars)
        self.post_.append((post_url, data))

    async def getiter(self, url):
        for item in self.getiter_:
            yield item


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
@pytest.mark.params(
    "path,expected,status_check",
    [
        ("news/3 Code Health/3684.md", True, news.Status.success),
        ("news/__pycache__/3684.md", False, news.Status.failure),
        ("news/3684.md", False, news.Status.failure),
        ("news/3 Code Health/3684.txt", False, news.Status.failure),
    ],
)
async def test_check_for_news_file(path, expected, status_check, monkeypatch):
    status_args = None

    async def status(*args):
        nonlocal status_args
        status_args = args

    monkeypatch.setattr(news, "status", status)
    event_data = json.loads(
        importlib_resources.read_text(samples, "pull_request-reopened-skip_news.json")
    )
    event = gidgethub.sansio.Event(event_data, event="pull_request", delivery_id="1")
    files_data = json.loads(
        importlib_resources.read_text(samples, "pull_request-files.json")
    )
    files_data[1]["filename"] = path
    gh = FakeGH(getiter_=files_data)
    assert await news.check_for_news_file(event, gh) == expected
    assert status_args[2] == status_check


@pytest.mark.asyncio
async def test_check_for_news(monkeypatch):
    status_args = None

    async def status(*args):
        nonlocal status_args
        status_args = args

    monkeypatch.setattr(news, "status", status)
    event_data = json.loads(
        importlib_resources.read_text(samples, "pull_request-reopened-skip_news.json")
    )
    event = gidgethub.sansio.Event(event_data, event="pull_request", delivery_id="1")
    files_data = json.loads(
        importlib_resources.read_text(samples, "pull_request-files.json")
    )
    original_file_path = files_data[1]["filename"]
    assert original_file_path == "news/3 Code Health/3684.md"
    files_data[1]["filename"] = "README"
    gh = FakeGH(getiter_=files_data)

    assert await news.check_for_news(event, gh)
    assert status_args[2] == news.Status.success

    event_data["pull_request"]["labels"] = []
    files_data[1]["filename"] = original_file_path
    status_args = None

    assert await news.check_for_news(event, gh)
    assert status_args[2] == news.Status.success

    files_data[1]["filename"] = "README"
    status_args = None

    assert not await news.check_for_news(event, gh)
    assert status_args[2] == news.Status.failure


# Also tests that the status check is initially set to "pending".
@pytest.mark.asyncio
@pytest.mark.params("action", ["opened", "reopened", "synchronize"])
async def test_PR_nonlabel_routing(action, monkeypatch):
    status_args = None

    async def status(*args):
        nonlocal status_args
        status_args = args

    monkeypatch.setattr(news, "status", status)

    async def check_for_skip_news_label(*args, **kwargs):
        return True

    monkeypatch.setattr(news, "check_for_skip_news_label", check_for_skip_news_label)

    event = gidgethub.sansio.Event(
        {"action": action}, event="pull_request", delivery_id="1"
    )

    await news.router.dispatch(event, object())
    assert status_args is not None  # We hit the route.
    assert status_args[2] == news.Status.pending


@pytest.mark.asyncio
async def test_PR_labeled_routing(monkeypatch):
    called = False

    def has_label(*args, **kwargs):
        nonlocal called
        called = True
        return False

    monkeypatch.setattr(news, "has_label", has_label)
    event = gidgethub.sansio.Event(
        {"action": "labeled"}, event="pull_request", delivery_id="1"
    )

    await news.router.dispatch(event, object())
    assert called


@pytest.mark.asyncio
async def test_PR_unlabeled_routing(monkeypatch):
    called = False

    def changed_label_matches(*args, **kwargs):
        nonlocal called
        called = True
        return False

    monkeypatch.setattr(news, "changed_label_matches", changed_label_matches)

    event = gidgethub.sansio.Event(
        {"action": "unlabeled"}, event="pull_request", delivery_id="1"
    )

    await news.router.dispatch(event, object())
    assert called
