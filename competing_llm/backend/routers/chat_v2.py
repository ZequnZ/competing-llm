import logging

from fastapi import APIRouter, HTTPException

from competing_llm.backend.configuration.model_registry import (
    AVAILABLE_LLMS,
    VALID_LLM_IDS,
    get_llm_info,
)
from competing_llm.backend.models.schema import (
    BatchChatRequest,
    BatchChatResponse,
    ChatRequest,
    ChatResponse,
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
            detail=f"Invalid LLM ID. Available: {', '.join(sorted(VALID_LLM_IDS))}",
        )

    llm_info = get_llm_info(request.llm_id)
    if not llm_info:
        raise HTTPException(status_code=404, detail="LLM not found")

    if request.api_provider != llm_info.api_provider:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid API provider for {request.llm_id}. "
                f"Expected: {llm_info.api_provider}"
            ),
        )

    response = await get_chat_completion(
        request.llm_id, request.api_provider, request.prompt
    )
    return response


@router.post("/completion/batch", response_model=BatchChatResponse)
async def batch_chat_completion(request: BatchChatRequest) -> BatchChatResponse:
    """
    Get complete chat responses from multiple LLMs concurrently.
    """
    # Validate all LLM IDs
    invalid_ids = [
        selection.llm_id
        for selection in request.llms
        if selection.llm_id not in VALID_LLM_IDS
    ]
    if invalid_ids:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid LLM IDs: {', '.join(invalid_ids)}. "
                f"Available: {', '.join(sorted(VALID_LLM_IDS))}"
            ),
        )

    provider_mismatches = []
    for selection in request.llms:
        llm_info = get_llm_info(selection.llm_id)
        if not llm_info:
            continue
        if selection.api_provider != llm_info.api_provider:
            provider_mismatches.append(
                f"{selection.llm_id} expects {llm_info.api_provider}"
            )

    if provider_mismatches:
        raise HTTPException(
            status_code=400,
            detail="; ".join(provider_mismatches),
        )

    responses = await get_batch_chat_completion(request.llms, request.prompt)
    return BatchChatResponse(responses=responses)
