
"""Optional sponsor calls. Their results never change payment authority."""

import json
import math
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException


SCHEDULER = Path(__file__).resolve().parents[1] / "node_modules/@bryntum/scheduler-trial"
SCHEDULER_ASSETS = {"scheduler.module.js", "scheduler.css", "stockholm-light.css"}


def settings(*names):
    return all(os.getenv(name) for name in names)


async def request(
    method,
    url,
    *,
    token=None,
    auth_scheme="Bearer",
    headers=None,
    body=None,
    timeout=20,
):
    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise HTTPException(503, "Sponsor endpoint must use HTTPS")

    headers = dict(headers or {})

    if token:
        headers["Authorization"] = f"{auth_scheme} {token}"

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=False,
        ) as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            return response

    except httpx.HTTPError:
        raise HTTPException(
            502,
            "Sponsor request failed or its outcome is unknown",
        ) from None


async def payload(*args, **kwargs):
    response = await request(*args, **kwargs)

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            502,
            "Sponsor returned invalid JSON",
        ) from None

    if not isinstance(data, dict):
        raise HTTPException(
            502,
            "Sponsor returned an unexpected response",
        )

    return data


def _safe_https_url(value):
    """Accept only absolute HTTPS URLs without embedded credentials."""

    if not isinstance(value, str):
        return None

    parsed = urlparse(value)

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        return None

    return value[:2000]


def _channel3_product(row):
    """Normalize a Channel3 product without trusting malformed fields."""

    if not isinstance(row, dict):
        return None

    product_id = row.get("id")
    title = row.get("title")

    if not isinstance(product_id, (str, int)) or not isinstance(title, str):
        return None

    product_id = str(product_id).strip()
    title = title.strip()

    if not product_id or not title:
        return None

    # Select the first usable product image.
    image_url = None
    images = row.get("images")

    if isinstance(images, list):
        for image in images:
            if not isinstance(image, dict):
                continue

            image_url = _safe_https_url(
                image.get("cleaned_url") or image.get("url")
            )

            if image_url:
                break

    # Normalize merchant offers.
    offers = []
    raw_offers = row.get("offers")

    if isinstance(raw_offers, list):
        for offer in raw_offers[:5]:
            if not isinstance(offer, dict):
                continue

            price = offer.get("price")

            if not isinstance(price, dict):
                continue

            amount = price.get("price")
            currency = price.get("currency")

            if (
                not isinstance(amount, (int, float))
                or isinstance(amount, bool)
                or not math.isfinite(amount)
                or amount < 0
                or not isinstance(currency, str)
                or not currency.strip()
            ):
                continue

            buy_url = _safe_https_url(offer.get("url"))

            if not buy_url:
                continue

            domain = offer.get("domain")
            availability = offer.get("availability")
            condition = offer.get("condition")

            offers.append({
                "url": buy_url,
                "merchant": domain[:120] if isinstance(domain, str) else "",
                "price": amount,
                "currency": currency.strip()[:10],
                "availability": (
                    availability[:30]
                    if isinstance(availability, str)
                    else "Unknown"
                ),
                "condition": (
                    condition[:30]
                    if isinstance(condition, str)
                    else None
                ),
            })

    description = row.get("description")

    return {
        "id": product_id[:100],
        "title": title[:180],
        "description": (
            description[:500]
            if isinstance(description, str)
            else ""
        ),
        "image_url": image_url,
        "offers": offers,
    }


async def channel3_search(query: str, limit: int = 8):
    """Search Channel3 and return normalized product discovery results."""

    if not isinstance(query, str):
        raise HTTPException(422, "Search query must be text")

    query = query.strip()

    if not query or len(query) > 200:
        raise HTTPException(
            422,
            "Search query must contain 1–200 characters",
        )

    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 10:
        raise HTTPException(
            422,
            "Limit must be between 1 and 10",
        )

    api_key = os.getenv("CHANNEL3_API_KEY")

    if not api_key:
        raise HTTPException(
            503,
            "Channel3 API key is not configured",
        )

    data = await payload(
        "POST",
        "https://api.trychannel3.com/v1/search",
        headers={"x-api-key": api_key},
        body={
            "query": query,
            "limit": limit,
        },
    )

    # Raw HTTP API response uses "products".
    # The SDK's .data/.items wrapper is not used here.
    products = data.get("products", data.get("data"))

    if not isinstance(products, list):
        raise HTTPException(
            502,
            "Channel3 returned an invalid products list",
        )

    results = []

    for row in products[:limit]:
        product = _channel3_product(row)

        if product:
            results.append(product)

    return results


async def channel3():
    """
    Preserve the existing sponsor evidence interface.

    Existing callers and tests expect a zero-argument function
    returning a list containing product IDs and titles.
    """

    products = await channel3_search(
        "Focusrite Scarlett 2i2 4th Gen audio interface",
        limit=5,
    )

    return [
        {
            "id": product["id"],
            "title": product["title"],
        }
        for product in products
    ]


async def elastic():
    data = await payload(
        "POST",
        os.environ["ELASTIC_URL"].rstrip("/") + "/assembly-evidence/_search",
        token=os.environ["ELASTIC_API_KEY"],
        auth_scheme="ApiKey",
        body={
            "size": 3,
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"variant": VARIANT}},
                        {"term": {"revision": REVISION}},
                    ]
                }
            },
        },
    )

    hits = data.get("hits", {}).get("hits", [])

    if not isinstance(hits, list):
        return []

    return [
        {
            "source": SOURCE,
            "excerpt": row["excerpt"][:1000],
        }
        for hit in hits
        if isinstance(hit, dict)
        and isinstance(row := hit.get("_source"), dict)
        and row.get("variant") == VARIANT
        and row.get("revision") == REVISION
        and row.get("source") == SOURCE
        and isinstance(row.get("excerpt"), str)
    ]


async def kernel():
    base = "https://api.onkernel.com"
    auth = {"token": os.environ["KERNEL_API_KEY"]}

    browser = await payload(
        "POST",
        base + "/browsers",
        body={"timeout_seconds": 60},
        **auth,
    )

    session = browser.get("session_id", "")

    if not isinstance(session, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]{1,100}",
        session,
    ):
        raise HTTPException(
            502,
            "Kernel did not return a browser session",
        )

    try:
        code = (
            "await page.route('**/*', route => route.request().url() === "
            + json.dumps(SOURCE)
            + " ? route.continue() : route.abort());"
            + "await page.goto("
            + json.dumps(SOURCE)
            + ", {waitUntil:'domcontentloaded'});"
            + "const text = await page.locator('body').innerText();"
            + "const i = text.indexOf('Neutrik'); "
            + "return i < 0 ? '' : text.slice(Math.max(0,i-80), i+300);"
        )

        result = await payload(
            "POST",
            f"{base}/browsers/{session}/playwright/execute",
            body={"code": code},
            **auth,
        )

        if (
            result.get("success") is False
            or not isinstance(result.get("result"), str)
        ):
            raise HTTPException(
                502,
                "Kernel could not read the approved source",
            )

        return {
            "session": session,
            "source": SOURCE,
            "excerpt": result["result"][:500],
        }

    finally:
        try:
            await request(
                "DELETE",
                f"{base}/browsers/{session}",
                timeout=5,
                **auth,
            )
        except HTTPException:
            pass  # The bounded browser lifetime also cleans up failed deletions.
        raise HTTPException(502, "Channel3 returned an invalid results list")
    return [{"id": str(row["id"])[:100], "title": str(row.get("title", ""))[:180]}
            for row in products[:5] if isinstance(row, dict) and row.get("id")]
