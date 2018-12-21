# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio

import gidgethub.sansio


async def serve(gh, router, headers, body, *, secret=None, logger=None, pause=1):
    """Process the webhook event based on the raw HTTP request."""
    event = gidgethub.sansio.Event.from_http(headers, body, secret=secret)
    if logger:
        logger.info(f"GitHub delivery ID: {event.delivery_id}")
    # Give GitHub some time to reach internal consistency.
    await asyncio.sleep(pause)
    await router.dispatch(event, gh, logger=logger)
    if logger:
        try:
            logger.info(f"GitHub requests remaining: {gh.rate_limit.remaining}")
        except AttributeError:
            logger.info("No rate limit data provided")
