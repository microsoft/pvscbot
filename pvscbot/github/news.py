import enum
import re

import gidgethub.routing

from .labels import Skip


router = gidgethub.routing.Router()


NEWS_PATH = re.compile(r"news/\d+ [^/]+/(?P<issue>\d+)(?P<nonce>-\S+)?\.md")


@enum.unique
class Status(enum.Enum):
    error = "error"
    failure = "failure"
    pending = "pending"
    success = "success"


async def status(event, gh, status, description):
    data = {
        "state": status.value,
        "target_url": "https://github.com/Microsoft/vscode-python/tree/master/news",
        "description": description,
        "context": "pvscbot/news",
    }
    await gh.post(event.data["pull_request"]["statuses_url"], data=data)


def has_label(event, label):
    label_names = (
        label_data["name"] for label_data in event.data["pull_request"]["labels"]
    )
    for label_name in label_names:
        if label_name == label.value:
            return True
    else:
        return False


def changed_label_matches(event, label):
    return event.data["label"]["name"] == label.value


async def PR_files(event, gh):
    url = event.data["pull_request"]["url"]
    async for path in gh.getiter(f"{url}/files"):
        yield path["filename"]


async def check_for_news_file(event, gh, *args, **kwargs):
    async for path in PR_files(event, gh):
        if NEWS_PATH.matches(path):
            await status(event, gh, Status.success, "news entry file found")
            return True
    else:
        await status(event, gh, Status.failure, "no news entry file found")
        return False


@router.register("pull_request", action="opened")
@router.register("pull_request", action="synchronize")
@router.register("pull_request", action="reopened")
async def check_for_news(event, gh, *args, **kwargs):
    await status(event, gh, Status.pending, "Looking for a news entry file")
    if await check_for_skip_news_label(event, gh, *args, **kwargs):
        return True
    else:
        return await check_for_news_file(event, gh, *args, **kwargs)


@router.register("pull_request", action="labeled")
async def check_for_skip_news_label(event, gh, *args, **kwargs):
    if has_label(event, Skip.news):
        await status(event, gh, Status.success, f"{Skip.news.value!r} label found")
        return True
    else:
        return False


@router.register("pull_request", action="unlabeled")
async def check_for_skip_news_label_removed(event, gh, *args, **kwargs):
    if changed_label_matches(event, Skip.news):
        await check_for_news_file(event, gh, *args, **kwargs)
