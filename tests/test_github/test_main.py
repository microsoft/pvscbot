import logging

import aiohttp
import asynctest
import azure.functions
import gidgethub.aiohttp
import gidgethub.routing
import pytest

from __app__ import github as github_main
from __app__.ghutils import server


@pytest.mark.asyncio
async def test_serve_call(monkeypatch):
    body = '{"action": "opened"}'.encode("UTF-8")
    secret = "123456"
    auth = "GitHub authorization"
    headers = {
        "content-type": "application/json",
        "x-github-event": "pull_request",
        "x-github-delivery": "72d3162e-cc78-11e3-81ab-4c9367dc0958",
        "x-hub-signature": "sha1=c28e33b2e56e548956c446e890929a6cbec3ac89",
    }

    request = azure.functions.HttpRequest(
        method="POST", url="...", headers=headers, body=body
    )

    monkeypatch.setenv("GH_AUTH", auth)
    monkeypatch.setenv("GH_SECRET", secret)
    mocked_serve = asynctest.create_autospec(server.serve)
    monkeypatch.setattr(server, "serve", mocked_serve)

    await github_main.main(request)

    assert mocked_serve.called
    assert mocked_serve.call_count == 1
    args, kwargs = mocked_serve.call_args
    given_gh, given_router, given_headers, given_body = args
    assert isinstance(given_gh, gidgethub.aiohttp.GitHubAPI)
    assert isinstance(github_main.CLIENT_SESSION, aiohttp.ClientSession)
    assert given_gh._session is github_main.CLIENT_SESSION
    assert given_gh.requester == "Microsoft/pvscbot"
    assert given_gh.oauth_token == auth
    assert given_router is github_main.router
    assert given_headers == headers
    assert given_body == body
    given_secret = kwargs["secret"]
    given_logger = kwargs["logger"]
    assert given_secret == secret
    assert given_logger is logging
