import asyncio
import logging
import random
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception for LLM mock errors."""

    pass


class RateLimitError(LLMError):
    """Simulated rate limit error."""

    pass


class LLMTimeoutError(LLMError):
    """Simulated timeout error."""

    pass


class LLMServiceError(LLMError):
    """Simulated service error."""

    pass


class MockLLMConfig:
    """Configuration for mock LLM behavior."""

    # Response length ranges per LLM ID
    RESPONSE_LENGTHS = {
        1: (30, 60),
        2: (70, 100),
        3: (50, 80),
        4: (40, 90),
        5: (60, 120),
    }

    # Error simulation probabilities (0.0 to 1.0)
    ERROR_RATES = {
        "rate_limit": 0.05,
        "timeout": 0.03,
        "service_error": 0.02,
    }

    # Delay ranges in seconds
    MIN_DELAY = 0.01
    MAX_DELAY = 0.1

    # Answer templates for common prompts
    ANSWER_TEMPLATES = {
        "hello": "Hello! I'm LLM {llm_id}, ready to assist you with your questions.",
        "help": "As LLM {llm_id}, I can help you with various tasks including answering questions, providing information, and assisting with problem-solving.",
        "weather": "LLM {llm_id} reports: The weather today is sunny with a temperature of 72°F. Perfect conditions for outdoor activities!",
        "code": "Here's a Python function from LLM {llm_id}:\n\ndef greet(name):\n    return f'Hello, {name}!'",
        "default": "This is a response from LLM {llm_id} providing insights on your query: {prompt}",
    }


async def mock_llm_stream(
    llm_id: int, prompt: str, delay: float = 0.05, config: MockLLMConfig | None = None
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Async generator that simulates LLM streaming responses.

    Args:
        llm_id: Identifier for the LLM model (1-5)
        prompt: User's input prompt
        delay: Base delay between chunks in seconds (default: 0.05)
        config: Optional configuration override

    Yields:
        Dict containing streaming chunk with format:
        {
            "chunk_id": int,
            "text": str,
            "timestamp": str (ISO format),
            "llm_id": int,
            "is_complete": bool
        }

    Raises:
        ValueError: If llm_id is invalid or prompt is empty
        RateLimitError: Simulated rate limiting
        LLMTimeoutError: Simulated timeout
        LLMServiceError: Simulated service error
    """
    if config is None:
        config = MockLLMConfig()

    # Validate inputs
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if llm_id not in config.RESPONSE_LENGTHS:
        raise ValueError(
            f"Invalid LLM ID: {llm_id}. Must be one of {list(config.RESPONSE_LENGTHS.keys())}"
        )

    # Simulate potential errors
    await _simulate_errors(config)

    # Generate response
    response_text = await _generate_response(llm_id, prompt, config)

    # Stream character by character
    chunk_id = 0
    for char in response_text:
        # Add realistic random delay
        actual_delay = max(0.001, delay + random.uniform(-delay / 2, delay / 2))
        actual_delay = max(config.MIN_DELAY, min(config.MAX_DELAY, actual_delay))
        await asyncio.sleep(actual_delay)

        chunk_id += 1
        chunk = {
            "chunk_id": chunk_id,
            "text": char,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "llm_id": llm_id,
            "is_complete": False,
        }

        yield chunk

    # Send completion signal
    completion_chunk = {
        "chunk_id": chunk_id + 1,
        "text": "",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "llm_id": llm_id,
        "is_complete": True,
    }
    yield completion_chunk


async def _simulate_errors(config: MockLLMConfig) -> None:
    """Simulate various error conditions based on configured probabilities."""
    rand = random.random()

    if rand < config.ERROR_RATES["rate_limit"]:
        raise RateLimitError("Rate limit exceeded. Please try again later.")

    if rand < config.ERROR_RATES["rate_limit"] + config.ERROR_RATES["timeout"]:
        raise LLMTimeoutError(
            "Request timed out. The LLM service is taking too long to respond."
        )

    if rand < sum(config.ERROR_RATES.values()):
        raise LLMServiceError(
            "LLM service is temporarily unavailable. Please try again later."
        )


async def _generate_response(llm_id: int, prompt: str, config: MockLLMConfig) -> str:
    """Generate a mock response based on the prompt and LLM ID."""
    prompt_lower = prompt.lower().strip()

    # Find matching template
    template_key = "default"
    for key in config.ANSWER_TEMPLATES:
        if key in prompt_lower:
            template_key = key
            break

    # Get base response
    base_response = config.ANSWER_TEMPLATES[template_key].format(
        llm_id=llm_id, prompt=prompt[:50] + "..." if len(prompt) > 50 else prompt
    )

    # Add LLM-specific variation
    min_len, max_len = config.RESPONSE_LENGTHS[llm_id]
    target_length = random.randint(min_len, max_len)

    # Adjust response length
    if len(base_response) < target_length:
        # Add additional content to reach target length
        additional = f" This response from LLM {llm_id} includes additional details to provide comprehensive assistance."
        base_response += additional[: target_length - len(base_response)]
    elif len(base_response) > target_length:
        # Truncate if too long
        base_response = base_response[:target_length]

    return base_response


async def batch_mock_llm_stream(
    llm_ids: list[int], prompt: str, delay: float = 0.05
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Stream responses from multiple LLMs concurrently.

    Args:
        llm_ids: List of LLM identifiers
        prompt: User's input prompt
        delay: Base delay between chunks

    Yields:
        Dict containing streaming chunk with additional 'source_llm' field
    """
    if not llm_ids:
        raise ValueError("At least one LLM ID must be provided")

    # Create tasks for concurrent streaming
    streams = []
    for llm_id in llm_ids:
        stream = mock_llm_stream(llm_id, prompt, delay)
        streams.append(stream)

    # Stream from all LLMs concurrently
    # This is a simplified version - in real implementation, you'd want
    # to interleave chunks from different LLMs
    for llm_id, stream in zip(llm_ids, streams):
        async for chunk in stream:
            chunk["source_llm"] = llm_id
            yield chunk


async def mock_llm_completion(
    llm_id: int, prompt: str, delay: float = 0.05, config: MockLLMConfig | None = None
) -> dict[str, Any]:
    """
    Generate a complete mock response without streaming.

    Args:
        llm_id: Identifier for the LLM model (1-5)
        prompt: User's input prompt
        delay: Factor to calculate processing time (default: 0.05)
        config: Optional configuration override

    Returns:
        Dict containing complete response

    Raises:
        ValueError: If llm_id is invalid or prompt is empty
        RateLimitError: Simulated rate limiting
        LLMTimeoutError: Simulated timeout
        LLMServiceError: Simulated service error
    """
    if config is None:
        config = MockLLMConfig()

    # Validate inputs
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if llm_id not in config.RESPONSE_LENGTHS:
        raise ValueError(
            f"Invalid LLM ID: {llm_id}. Must be one of {list(config.RESPONSE_LENGTHS.keys())}"
        )

    # Simulate potential errors
    await _simulate_errors(config)

    # Generate response
    response_text = await _generate_response(llm_id, prompt, config)

    # Simulate "thinking" time based on length and delay
    # Cap at 2 seconds to ensure good UX for non-streaming
    processing_time = len(response_text) * (delay / 2)
    await asyncio.sleep(min(processing_time, 2.0))

    return {
        "llm_id": llm_id,
        "prompt": prompt,
        "content": response_text,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


async def batch_mock_llm_completion(
    llm_ids: list[int], prompt: str, delay: float = 0.05
) -> list[dict[str, Any]]:
    """
    Get complete responses from multiple LLMs concurrently.

    Args:
        llm_ids: List of LLM identifiers
        prompt: User's input prompt
        delay: Factor for processing time

    Returns:
        List of Dicts containing complete responses
    """
    if not llm_ids:
        raise ValueError("At least one LLM ID must be provided")

    # Create tasks for concurrent execution
    tasks = []
    for llm_id in llm_ids:
        tasks.append(mock_llm_completion(llm_id, prompt, delay))

    return await asyncio.gather(*tasks)
