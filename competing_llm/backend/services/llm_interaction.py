import asyncio
import logging

from competing_llm.backend.configuration.model_registry import get_llm_info
from competing_llm.backend.models.schema import ChatResponse, LLMSelection
from competing_llm.backend.utils.llm_utils import create_async_llm_client

logger = logging.getLogger(__name__)


async def get_chat_completion(
    llm_id: str, api_provider: str, prompt: str
) -> ChatResponse:
    """
    Get a chat completion from a specific LLM.

    Args:
        llm_id: The model identifier (deployment name)
        prompt: The user prompt
        api_provider: The API provider (Azure OpenAI or OpenRouter)
    Returns:
        ChatResponse object containing the response content or error
    """
    client = create_async_llm_client(api_provider)

    try:
        messages = [{"role": "user", "content": prompt}]

        # Determine model configuration
        llm_info = get_llm_info(llm_id)
        is_reasoning = llm_info.reasoning_model if llm_info else False

        if is_reasoning:
            # Reasoning models use the Responses API
            kwargs = {
                "model": llm_id,
                "input": messages,
                "reasoning": {"effort": "minimal"},
            }
            response = await client.responses.parse(**kwargs)
            content = response.output_text
        else:
            # Standard models use Chat Completions API
            kwargs = {
                "model": llm_id,
                "messages": messages,
                "temperature": 0.7,
            }
            response = await client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content
        return ChatResponse(llm_id=llm_id, content=content)

    except Exception as e:
        logger.error(f"Error calling LLM {llm_id}: {str(e)}")
        return ChatResponse(
            llm_id=llm_id, content="", error=f"Failed to generate response: {str(e)}"
        )
    finally:
        await client.close()


async def get_batch_chat_completion(
    llms: list[LLMSelection], prompt: str
) -> list[ChatResponse]:
    """
    Get chat completions from multiple LLMs in parallel.

    Args:
        llms: List of model/provider selections
        prompt: The user prompt

    Returns:
        List of ChatResponse objects
    """
    # Create tasks for all LLMs
    tasks = [
        get_chat_completion(selection.llm_id, selection.api_provider, prompt)
        for selection in llms
    ]

    # Run tasks concurrently
    results = await asyncio.gather(*tasks)

    return list(results)
