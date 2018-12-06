import os

import azure.functions as func
from azure.functions_worker.bindings import http, meta
import pytest

from ... import github


@pytest.mark.asyncio
async def test_missing_environment_variables():
    body = '{"zen": "Speak like a human."}'
    secret = "123456"
    headers = {
        "content-type": "application/json",
        "x-github-event": "ping",
        "x-github-delivery": "72d3162e-cc78-11e3-81ab-4c9367dc0958",
        "x-hub-signature": "sha1=c28e33b2e56e548956c446e890929a6cbec3ac89",
    }

    request = http.HttpRequest(
        "POST",
        "some/url",
        headers=headers,
        params={},
        route_params={},
        body_type=meta.TypedDataKind.json,
        body=body,
    )

    response = await github.main(request)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_ping(monkeypatch):
    body = '{"zen": "Speak like a human."}'
    secret = "123456"
    headers = {
        "content-type": "application/json",
        "x-github-event": "ping",
        "x-github-delivery": "72d3162e-cc78-11e3-81ab-4c9367dc0958",
        "x-hub-signature": "sha1=33ddc4828233bb203afb0463a9f1e64fea8f9c9d",
    }

    monkeypatch.setattr(
        os, "environ", {"GH_SECRET": secret, "GH_AUTH": "I'm a good person!"}
    )

    request = http.HttpRequest(
        "POST",
        "some/url",
        headers=headers,
        params={},
        route_params={},
        body_type=meta.TypedDataKind.json,
        body=body,
    )

    response = await github.main(request)
    assert response.status_code == 200
