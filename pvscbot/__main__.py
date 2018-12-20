import asyncio
import importlib
import logging
import os
import sys
import traceback

import aiohttp
from aiohttp import web
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing
from gidgethub import sansio

from .ghutils import server
from .github import classify, closed, news


router = routing.Router(classify.router, closed.router, news.router)


async def hello(_):
    return web.Response(text="Hello, world")


async def main(request):
    try:
        body = await request.body()
        secret = os.environ.get("GH_SECRET")
        oauth_token = os.environ.get("GH_AUTH")
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(
                session, "python/bedevere", oauth_token=oauth_token
            )
            await server.serve(
                gh, router, request.headers, body, secret=secret, logger=logging
            )
        return web.Response(status=200)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_get("/", hello)
    app.router.add_post("/github", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)
    web.run_app(app, port=port)
