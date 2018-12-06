# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
import os

import aiohttp
import azure.functions as func
import gidgethub.aiohttp
import gidgethub.routing
import gidgethub.sansio

from ..ghutils import server
from ..ghutils import ping


router = gidgethub.routing.Router(ping.router)


async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        secret = os.environ.get("GH_SECRET")
        oauth_token = os.environ.get("GH_AUTH")
        async with aiohttp.ClientSession() as session:
            gh = gidgethub.aiohttp.GitHubAPI(
                session, "microsoft/pvsc-bot", oauth_token=oauth_token
            )
            await server.serve(
                gh, router, req.headers, req.get_body(), secret=secret, logger=logging
            )
        return func.HttpResponse(status_code=200)
    except Exception:
        logging.error("General exception raised", exc_info=True)
    return func.HttpResponse("internal server error", status_code=500)
