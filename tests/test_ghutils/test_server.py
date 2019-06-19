# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import gidgethub.routing
import pytest

from __app__.ghutils import server


class Logger:
    def __init__(self):
        self._logged = []

    def info(self, message):
        self._logged.append(message)


@pytest.mark.asyncio
async def test_event_creation_and_routing():
    body = '{"action": "opened"}'.encode("UTF-8")
    secret = "123456"
    headers = {
        "content-type": "application/json",
        "x-github-event": "pull_request",
        "x-github-delivery": "72d3162e-cc78-11e3-81ab-4c9367dc0958",
        "x-hub-signature": "sha1=c28e33b2e56e548956c446e890929a6cbec3ac89",
    }
    router = gidgethub.routing.Router()
    gh = object()
    logger = Logger()
    route_hit = None

    @router.register("pull_request", action="opened")
    async def routed(*args, **kwargs):
        nonlocal route_hit
        route_hit = args, kwargs

    await server.serve(gh, router, headers, body, secret=secret, logger=logger, pause=0)
    assert route_hit[0][0].event == "pull_request"  # Test event creation.
    assert route_hit[0][1] == gh  # Test routing.
    assert route_hit[1]["logger"] is logger  # Test logger passed into routes.


@pytest.mark.asyncio
async def test_logging():
    body = '{"action": "opened"}'.encode("UTF-8")
    secret = "123456"
    headers = {
        "content-type": "application/json",
        "x-github-event": "pull_request",
        "x-github-delivery": "72d3162e-cc78-11e3-81ab-4c9367dc0958",
        "x-hub-signature": "sha1=c28e33b2e56e548956c446e890929a6cbec3ac89",
    }
    router = gidgethub.routing.Router()
    gh = object()
    logger = Logger()

    await server.serve(gh, router, headers, body, secret=secret, logger=logger, pause=0)
    assert headers["x-github-delivery"] in logger._logged[0]

    # Setting a logger is optional.
    await server.serve(gh, router, headers, body, secret=secret, logger=None, pause=0)
