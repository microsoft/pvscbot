import asyncio
import logging
import os

import aiohttp
import azure.functions as func
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing

from ..ghutils import ping
from ..ghutils import server
from . import classify, closed


router = routing.Router(classify.router, closed.router, ping.router)

CLIENT_SESSION = None


async def main(req: func.HttpRequest) -> func.HttpResponse:
    global CLIENT_SESSION

    try:
        if CLIENT_SESSION is None:
            CLIENT_SESSION = aiohttp.ClientSession()
        secret = os.environ.get("GH_SECRET")
        oauth_token = os.environ.get("GH_AUTH")
        body = req.get_body()
        gh = gh_aiohttp.GitHubAPI(
            CLIENT_SESSION, "Microsoft/pvscbot", oauth_token=oauth_token
        )
        await server.serve(gh, router, req.headers, body, secret=secret, logger=logging)
        return func.HttpResponse(status_code=200)
    except Exception:
        logging.exception("Unhandled exception")
        return func.HttpResponse(status_code=500)
