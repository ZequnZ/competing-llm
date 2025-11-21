import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from ..models.llm import (
    BatchChatRequest,
    BatchChatResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LLMInfo,
    LLMListResponse,
)
from ..services.llm_mock import (
    LLMServiceError,
    LLMTimeoutError,
    RateLimitError,
    batch_mock_llm_completion,
    batch_mock_llm_stream,
    mock_llm_completion,
    mock_llm_stream,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/completion", response_model=ChatResponse)
async def chat_completion(request: ChatRequest) -> ChatResponse:
    """
    Get a complete chat response from a single LLM (non-streaming).

    Args:
        request: ChatRequest containing prompt, llm_id, and optional delay

    Returns:
        ChatResponse with complete text content
    """
    try:
        result = await mock_llm_completion(
            request.llm_id, request.prompt, request.delay
        )
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except LLMTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except LLMServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat_completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/completion/batch", response_model=BatchChatResponse)
async def batch_chat_completion(request: BatchChatRequest) -> BatchChatResponse:
    """
    Get complete chat responses from multiple LLMs concurrently (non-streaming).

    Args:
        request: BatchChatRequest containing prompt, llm_ids, and optional delay

    Returns:
        BatchChatResponse with list of complete responses
    """
    try:
        results = await batch_mock_llm_completion(
            request.llm_ids, request.prompt, request.delay
        )
        return BatchChatResponse(
            responses=[ChatResponse(**r) for r in results],
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in batch_chat_completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stream")
async def stream_chat(request: ChatRequest) -> EventSourceResponse:
    """
    Stream a chat response from a single LLM using Server-Sent Events.

    Args:
        request: ChatRequest containing prompt, llm_id, and optional delay

    Returns:
        EventSourceResponse with streaming text chunks
    """
    try:
        return EventSourceResponse(
            _stream_single_llm(request.llm_id, request.prompt, request.delay),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in stream_chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stream/batch")
async def stream_batch_chat(request: BatchChatRequest) -> EventSourceResponse:
    """
    Stream chat responses from multiple LLMs concurrently using Server-Sent Events.

    Args:
        request: BatchChatRequest containing prompt, llm_ids, and optional delay

    Returns:
        EventSourceResponse with streaming text chunks from multiple LLMs
    """
    try:
        return EventSourceResponse(
            _stream_batch_llms(request.llm_ids, request.prompt, request.delay),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in stream_batch_chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check() -> HealthResponse:
    """
    Health check endpoint for the chat service.

    Returns:
        HealthResponse with service status and available LLMs
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        available_llms=[1, 2, 3, 4, 5],
        version="1.0.0",
    )


@router.get("/llms")
async def list_llms() -> LLMListResponse:
    """
    Get information about all available LLMs.

    Returns:
        LLMListResponse with details about each available LLM
    """
    llms = [
        LLMInfo(
            llm_id=1,
            name="GPT-3.5 Turbo",
            description="Fast and efficient language model suitable for general conversations",
            avg_response_length="30-60 characters",
            speed_rating="Fast",
        ),
        LLMInfo(
            llm_id=2,
            name="GPT-4",
            description="Advanced language model with superior reasoning capabilities",
            avg_response_length="70-100 characters",
            speed_rating="Medium",
        ),
        LLMInfo(
            llm_id=3,
            name="Claude-3 Haiku",
            description="Balanced model with good performance and speed",
            avg_response_length="50-80 characters",
            speed_rating="Medium",
        ),
        LLMInfo(
            llm_id=4,
            name="Llama-2 7B",
            description="Open-source model with decent performance",
            avg_response_length="40-90 characters",
            speed_rating="Medium",
        ),
        LLMInfo(
            llm_id=5,
            name="Gemini Pro",
            description="Google's advanced model with multimodal capabilities",
            avg_response_length="60-120 characters",
            speed_rating="Slow",
        ),
    ]

    return LLMListResponse(llms=llms, total_count=len(llms))


async def _stream_single_llm(
    llm_id: int, prompt: str, delay: float
) -> AsyncGenerator[dict, None]:
    """Internal generator for single LLM streaming."""
    try:
        async for chunk in mock_llm_stream(llm_id, prompt, delay):
            yield {"event": "chunk", "data": json.dumps(chunk)}

    except RateLimitError as e:
        error_response = {
            "error": "rate_limit",
            "message": str(e),
            "timestamp": asyncio.get_event_loop().time(),
            "llm_id": llm_id,
        }
        yield {"event": "error", "data": json.dumps(error_response)}

    except LLMTimeoutError as e:
        error_response = {
            "error": "timeout",
            "message": str(e),
            "timestamp": asyncio.get_event_loop().time(),
            "llm_id": llm_id,
        }
        yield {"event": "error", "data": json.dumps(error_response)}

    except LLMServiceError as e:
        error_response = {
            "error": "service_error",
            "message": str(e),
            "timestamp": asyncio.get_event_loop().time(),
            "llm_id": llm_id,
        }
        yield {"event": "error", "data": json.dumps(error_response)}

    except Exception as e:
        logger.error(f"Unexpected error in _stream_single_llm: {str(e)}")
        error_response = {
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "timestamp": asyncio.get_event_loop().time(),
            "llm_id": llm_id,
        }
        yield {"event": "error", "data": json.dumps(error_response)}


async def _stream_batch_llms(
    llm_ids: list[int], prompt: str, delay: float
) -> AsyncGenerator[dict, None]:
    """Internal generator for batch LLM streaming."""
    try:
        async for chunk in batch_mock_llm_stream(llm_ids, prompt, delay):
            yield {"event": "chunk", "data": json.dumps(chunk)}

    except Exception as e:
        logger.error(f"Error in _stream_batch_llms: {str(e)}")
        error_response = {
            "error": "batch_error",
            "message": str(e),
            "timestamp": asyncio.get_event_loop().time(),
        }
        yield {"event": "error", "data": json.dumps(error_response)}
