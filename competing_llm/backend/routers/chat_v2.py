import logging
from typing import List

from fastapi import APIRouter, HTTPException

from competing_llm.backend.configuration.model_registry import AVAILABLE_LLMS, VALID_LLM_IDS
from competing_llm.backend.models.schema import (
    BatchChatRequest,
    BatchChatResponse,
    ChatRequest,
    ChatResponse,
    LLMInfo,
    LLMListResponse,
)
from competing_llm.backend.services.llm_interaction import (
    get_batch_chat_completion,
    get_chat_completion,
)

router = APIRouter(prefix="/api/v2/chat", tags=["chat-v2"])

logger = logging.getLogger(__name__)


@router.get("/llms", response_model=LLMListResponse)
async def list_llms() -> LLMListResponse:
    """
    Get information about all available LLMs.
    """
    return LLMListResponse(llms=AVAILABLE_LLMS, total_count=len(AVAILABLE_LLMS))


@router.post("/completion", response_model=ChatResponse)
async def chat_completion(request: ChatRequest) -> ChatResponse:
    """
    Get a complete chat response from a single LLM.
    """
    if request.llm_id not in VALID_LLM_IDS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid LLM ID. Available: {', '.join(VALID_LLM_IDS)}"
        )
        
    response = await get_chat_completion(request.llm_id, request.prompt)
    return response


@router.post("/completion/batch", response_model=BatchChatResponse)
async def batch_chat_completion(request: BatchChatRequest) -> BatchChatResponse:
    """
    Get complete chat responses from multiple LLMs concurrently.
    """
    # Validate all LLM IDs
    invalid_ids = [lid for lid in request.llm_ids if lid not in VALID_LLM_IDS]
    if invalid_ids:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid LLM IDs: {', '.join(invalid_ids)}. Available: {', '.join(VALID_LLM_IDS)}"
        )
        
    responses = await get_batch_chat_completion(request.llm_ids, request.prompt)
    return BatchChatResponse(responses=responses)
