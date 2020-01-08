# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import json
import logging
import os
import sys

import aiohttp
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing
from gidgethub import sansio

from .github import classify, closed, news


router = routing.Router(classify.router, closed.router, news.router)


async def main():
    oauth_token = os.environ.get("INPUT_REPO-TOKEN", sys.argv[1])
    webhook_event_name = os.environ["GITHUB_EVENT_NAME"]
    webhook_path = os.environ["GITHUB_EVENT_PATH"]
    with open(webhook_path, "r", encoding="utf-8") as file:
        webhook_payload = json.load(file)
    webhook_event = sansio.Event(
        webhook_payload, event=webhook_event_name, delivery_id="<unknown>"
    )
    repo = os.environ["GITHUB_REPOSITORY"]
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, repo, oauth_token=oauth_token)
        await router.dispatch(webhook_event, gh, logger=logging)


if __name__ == "__main__":
    asyncio.run(main())
