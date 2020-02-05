# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import gidgethub.sansio
import pytest

from __app__.ghutils import ping


class Logger:
    def __init__(self):
        self._logged = []

    def info(self, message):
        self._logged.append(message)


@pytest.mark.asyncio
async def test_ping():
    gh = object()
    event = gidgethub.sansio.Event({}, event="ping", delivery_id="12345")
    await ping.router.dispatch(event, gh)


@pytest.mark.asyncio
async def test_ping_logging():
    logger = Logger()
    gh = object()
    event = gidgethub.sansio.Event({}, event="ping", delivery_id="12345")

    await ping.router.dispatch(event, gh, logger=logger)
    assert len(logger._logged) == 1
    assert "ping" in logger._logged[0]
