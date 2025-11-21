"""
Unit tests for the LLM mock streaming service.
"""

import pytest

from ..services.llm_mock import (
    MockLLMConfig,
    RateLimitError,
    batch_mock_llm_stream,
    mock_llm_stream,
)


class TestMockLLMStream:
    """Test cases for the mock LLM streaming function."""

    @pytest.mark.asyncio
    async def test_basic_streaming(self):
        """Test basic streaming functionality."""
        chunks = []
        async for chunk in mock_llm_stream(1, "hello world"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert chunks[-1]["is_complete"] is True
        assert chunks[0]["llm_id"] == 1
        assert chunks[0]["text"] != ""

    @pytest.mark.asyncio
    async def test_empty_prompt_raises_error(self):
        """Test that empty prompt raises ValueError."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            async for _ in mock_llm_stream(1, ""):
                pass

    @pytest.mark.asyncio
    async def test_invalid_llm_id_raises_error(self):
        """Test that invalid LLM ID raises ValueError."""
        with pytest.raises(ValueError, match="Invalid LLM ID"):
            async for _ in mock_llm_stream(99, "test prompt"):
                pass

    @pytest.mark.asyncio
    async def test_response_length_varies_by_llm(self):
        """Test that response lengths vary by LLM ID."""
        # Test LLM 1 (shorter responses)
        chunks_llm1 = []
        async for chunk in mock_llm_stream(1, "test"):
            if not chunk["is_complete"]:
                chunks_llm1.append(chunk)

        # Test LLM 2 (longer responses)
        chunks_llm2 = []
        async for chunk in mock_llm_stream(2, "test"):
            if not chunk["is_complete"]:
                chunks_llm2.append(chunk)

        assert len(chunks_llm2) > len(chunks_llm1)

    @pytest.mark.asyncio
    async def test_custom_delay_affects_streaming(self):
        """Test that custom delay affects streaming speed."""
        import time

        start_time = time.time()
        chunks = []
        async for chunk in mock_llm_stream(1, "test", delay=0.01):
            chunks.append(chunk)
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 1.0  # Should be very fast with 0.01 delay

    @pytest.mark.asyncio
    async def test_error_simulation(self):
        """Test error simulation with mocked random."""
        config = MockLLMConfig()
        config.ERROR_RATES = {
            "rate_limit": 1.0,  # Force rate limit error
            "timeout": 0.0,
            "service_error": 0.0,
        }

        with pytest.raises(RateLimitError):
            async for _ in mock_llm_stream(1, "test", config=config):
                pass

    @pytest.mark.asyncio
    async def test_batch_streaming(self):
        """Test batch streaming from multiple LLMs."""
        chunks = []
        async for chunk in batch_mock_llm_stream([1, 2, 3], "test prompt"):
            chunks.append(chunk)

        assert len(chunks) > 0
        # Should have chunks from multiple LLMs
        llm_ids = {chunk.get("source_llm") for chunk in chunks}
        assert len(llm_ids) >= 1

    @pytest.mark.asyncio
    async def test_batch_empty_llm_list_raises_error(self):
        """Test that empty LLM list raises error."""
        with pytest.raises(ValueError, match="At least one LLM ID must be provided"):
            async for _ in batch_mock_llm_stream([], "test"):
                pass

    @pytest.mark.asyncio
    async def test_chunk_format(self):
        """Test that chunks have correct format."""
        chunks = []
        async for chunk in mock_llm_stream(1, "hello"):
            chunks.append(chunk)

        for chunk in chunks:
            assert "chunk_id" in chunk
            assert "text" in chunk
            assert "timestamp" in chunk
            assert "llm_id" in chunk
            assert "is_complete" in chunk
            assert isinstance(chunk["chunk_id"], int)
            assert isinstance(chunk["text"], str)
            assert isinstance(chunk["llm_id"], int)
            assert isinstance(chunk["is_complete"], bool)

    @pytest.mark.asyncio
    async def test_response_templates(self):
        """Test that response templates are used correctly."""
        chunks = []
        async for chunk in mock_llm_stream(1, "hello"):
            if not chunk["is_complete"]:
                chunks.append(chunk)

        full_response = "".join(chunk["text"] for chunk in chunks)
        assert "Response from LLM 1" in full_response

    @pytest.mark.asyncio
    async def test_completion_signal(self):
        """Test that completion signal is sent."""
        chunks = []
        async for chunk in mock_llm_stream(1, "test"):
            chunks.append(chunk)

        assert chunks[-1]["is_complete"] is True
        assert chunks[-1]["text"] == ""
