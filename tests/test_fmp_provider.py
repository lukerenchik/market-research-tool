import asyncio
import time

import httpx
import pytest

from market_intelligence.ingestion.providers.fmp import FMP_BASE_URL, FMPProvider, RateLimiter


def make_provider(handler) -> FMPProvider:
    """An FMPProvider whose HTTP client is routed to `handler` instead of the network."""
    provider = FMPProvider(api_key="test-key", calls_per_minute=60_000)
    provider.client = httpx.AsyncClient(
        base_url=FMP_BASE_URL, transport=httpx.MockTransport(handler)
    )
    return provider


async def test_requests_hit_expected_endpoint_with_symbol_and_api_key():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=[{"symbol": "AAPL"}])

    provider = make_provider(handler)
    result = await provider.get_key_metrics("AAPL")
    await provider.close()

    assert result == [{"symbol": "AAPL"}]
    (request,) = seen
    assert request.url.path.endswith("/key-metrics")
    assert request.url.params["symbol"] == "AAPL"
    assert request.url.params["apikey"] == "test-key"


async def test_http_errors_are_raised_not_swallowed():
    provider = make_provider(lambda request: httpx.Response(429, json={"error": "rate limited"}))
    with pytest.raises(httpx.HTTPStatusError):
        await provider.get_stock_quote("AAPL")
    await provider.close()


async def test_rate_limiter_enforces_minimum_spacing():
    limiter = RateLimiter(calls_per_minute=600)  # one call every 0.1s
    assert limiter.min_interval == pytest.approx(0.1)

    start = time.monotonic()
    for _ in range(3):
        await limiter.acquire()
    elapsed = time.monotonic() - start

    # The first call goes through immediately; the next two each wait ~0.1s.
    assert elapsed >= 0.19


async def test_rate_limiter_serializes_concurrent_callers():
    limiter = RateLimiter(calls_per_minute=600)
    start = time.monotonic()
    await asyncio.gather(*(limiter.acquire() for _ in range(3)))
    assert time.monotonic() - start >= 0.19
