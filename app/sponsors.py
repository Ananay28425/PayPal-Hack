"""Optional sponsor calls. Their results never change payment authority."""
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException


SCHEDULER = Path(__file__).resolve().parents[1] / "node_modules/@bryntum/scheduler-trial"
SCHEDULER_ASSETS = {"scheduler.module.js", "scheduler.css", "stockholm-light.css"}


def settings(*names):
    return all(os.getenv(name) for name in names)


async def request(method, url, *, token=None, auth_scheme="Bearer", headers=None, body=None, timeout=20):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(503, "Sponsor endpoint must use HTTPS")
    headers = dict(headers or {})
    if token:
        headers["Authorization"] = f"{auth_scheme} {token}"
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            response = await client.request(method, url, headers=headers, json=body)
            response.raise_for_status()
            return response
    except httpx.HTTPError:
        raise HTTPException(502, "Sponsor request failed or its outcome is unknown") from None


async def payload(*args, **kwargs):
    response = await request(*args, **kwargs)
    try:
        data = response.json()
    except ValueError:
        raise HTTPException(502, "Sponsor returned invalid JSON") from None
    if not isinstance(data, dict):
        raise HTTPException(502, "Sponsor returned an unexpected response")
    return data


async def channel3():
    data = await payload("POST", "https://api.trychannel3.com/v1/search",
                         headers={"x-api-key": os.environ["CHANNEL3_API_KEY"]},
                         body={"query": "Focusrite Scarlett 2i2 4th Gen audio interface", "limit": 5})
    products = data.get("data")
    if not isinstance(products, list):
        raise HTTPException(502, "Channel3 returned an invalid results list")
    return [{"id": str(row["id"])[:100], "title": str(row.get("title", ""))[:180]}
            for row in products[:5] if isinstance(row, dict) and row.get("id")]
