"""
Integration tests for the chat API endpoints.
"""

import pytest
from httpx import AsyncClient

from ..app import app


class TestChatAPI:
    """Integration tests for chat API endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/chat/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "available_llms" in data
            assert isinstance(data["available_llms"], list)

    @pytest.mark.asyncio
    async def test_list_llms(self):
        """Test LLM listing endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/chat/llms")
            assert response.status_code == 200
            data = response.json()
            assert "llms" in data
            assert "total_count" in data
            assert isinstance(data["llms"], list)
            assert len(data["llms"]) == data["total_count"]

            # Check structure of first LLM
            llm = data["llms"][0]
            assert "llm_id" in llm
            assert "name" in llm
            assert "description" in llm
            assert "avg_response_length" in llm
            assert "speed_rating" in llm

    @pytest.mark.asyncio
    async def test_stream_chat_valid_request(self):
        """Test streaming chat with valid request."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream", json={"prompt": "hello", "llm_id": 1, "delay": 0.01}
            )
            assert response.status_code == 200
            assert (
                response.headers["content-type"] == "text/event-stream; charset=utf-8"
            )

    @pytest.mark.asyncio
    async def test_stream_chat_empty_prompt(self):
        """Test streaming chat with empty prompt."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream", json={"prompt": "", "llm_id": 1}
            )
            assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.asyncio
    async def test_stream_chat_invalid_llm_id(self):
        """Test streaming chat with invalid LLM ID."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream", json={"prompt": "hello", "llm_id": 99}
            )
            assert response.status_code == 400
            assert "Invalid LLM ID" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_stream_batch_valid_request(self):
        """Test batch streaming with valid request."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream/batch",
                json={"prompt": "hello", "llm_ids": [1, 2, 3], "delay": 0.01},
            )
            assert response.status_code == 200
            assert (
                response.headers["content-type"] == "text/event-stream; charset=utf-8"
            )

    @pytest.mark.asyncio
    async def test_stream_batch_empty_llm_list(self):
        """Test batch streaming with empty LLM list."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream/batch", json={"prompt": "hello", "llm_ids": []}
            )
            assert response.status_code == 400
            assert "At least one LLM ID must be provided" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "Welcome to competing-llm API" in data["message"]

    @pytest.mark.asyncio
    async def test_app_health_check(self):
        """Test application health check."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "competing-llm-api"
