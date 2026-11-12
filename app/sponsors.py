"""Optional sponsor calls. Their results never change payment authority."""
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException


SOURCE = "https://userguides.focusrite.com/hc/en-gb/articles/19640392541202-Scarlett-2i2-4th-Gen-Specifications"
VARIANT = "scarlett-2i2-4th-gen"
REVISION = "manufacturer-reference-v1"
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


async def elastic():
    data = await payload("POST", os.environ["ELASTIC_URL"].rstrip("/") + "/assembly-evidence/_search",
                         token=os.environ["ELASTIC_API_KEY"], auth_scheme="ApiKey",
                         body={"size": 3, "query": {"bool": {"filter": [
                             {"term": {"variant": VARIANT}}, {"term": {"revision": REVISION}},
                         ]}}})
    hits = data.get("hits", {}).get("hits", [])
    return [{"source": SOURCE, "excerpt": row["excerpt"][:1000]}
            for hit in hits if isinstance(row := hit.get("_source"), dict)
            and row.get("variant") == VARIANT and row.get("revision") == REVISION
            and row.get("source") == SOURCE and isinstance(row.get("excerpt"), str)]


async def kernel():
    base = "https://api.onkernel.com"
    auth = {"token": os.environ["KERNEL_API_KEY"]}
    browser = await payload("POST", base + "/browsers", body={"timeout_seconds": 60}, **auth)
    session = browser.get("session_id", "")
    if not isinstance(session, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", session):
        raise HTTPException(502, "Kernel did not return a browser session")
    try:
        code = ("await page.route('**/*', route => route.request().url() === "
                + json.dumps(SOURCE) + " ? route.continue() : route.abort());"
                + "await page.goto(" + json.dumps(SOURCE) + ", {waitUntil:'domcontentloaded'});"
                + "const text = await page.locator('body').innerText();"
                + "const i = text.indexOf('Neutrik'); return i < 0 ? '' : text.slice(Math.max(0,i-80), i+300);")
        result = await payload("POST", f"{base}/browsers/{session}/playwright/execute",
                               body={"code": code}, **auth)
        if result.get("success") is False or not isinstance(result.get("result"), str):
            raise HTTPException(502, "Kernel could not read the approved source")
        return {"session": session, "source": SOURCE, "excerpt": result["result"][:500]}
    finally:
        try:
            await request("DELETE", f"{base}/browsers/{session}", timeout=5, **auth)
        except HTTPException:
            pass  # The bounded browser lifetime also cleans up failed deletions.
