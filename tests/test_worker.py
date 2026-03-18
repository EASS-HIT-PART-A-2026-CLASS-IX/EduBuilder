import anyio
import pytest
from unittest.mock import AsyncMock

from scripts.refresh import generate_digest_for_course, process_course


@pytest.mark.anyio
async def test_generate_digest_without_api_key_returns_mocked_digest():
    digest = await generate_digest_for_course("proj_id", "Test Course", "Test content")
    assert digest is not None
    assert "Test Course" in digest


@pytest.mark.anyio
async def test_process_course_uses_idempotency(monkeypatch):
    class MockRedis:
        def __init__(self):
            self.store = {}

        async def get(self, key):
            return self.store.get(key)

        async def setex(self, key, time, value):
            self.store[key] = value

    mock_redis = MockRedis()
    monkeypatch.setattr("scripts.refresh.redis", mock_redis)
    monkeypatch.setattr("scripts.refresh.save_digest_to_db", lambda course_id, digest: None)

    async def mock_generate(*args):
        return "New Digest"

    monkeypatch.setattr("scripts.refresh.generate_digest_for_course", mock_generate)

    limiter = anyio.CapacityLimiter(3)

    await process_course("proj_id", "Test title", "Test content", limiter)
    assert await mock_redis.get("course_digest_processed:proj_id") == "1"

    monkeypatch.setattr(
        "scripts.refresh.generate_digest_for_course",
        AsyncMock(side_effect=Exception("Should not be called")),
    )
    await process_course("proj_id", "Test title", "Test content", limiter)
