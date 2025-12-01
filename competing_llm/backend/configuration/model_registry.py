from competing_llm.backend.models.schema import LLMInfo

# Define available LLMs
AVAILABLE_LLMS = [
    LLMInfo(
        llm_id="gpt-5-nano",
        provider="OpenAI",
        api_provider="Azure OpenAI",
        name="GPT-5 Nano",
        description="Next-gen efficient model with reasoning capabilities",
        avg_response_length="Medium",
        speed_rating="Fast",
        reasoning_model=True,
    ),
    LLMInfo(
        llm_id="gpt-4.1",
        provider="OpenAI",
        api_provider="Azure OpenAI",
        name="GPT-4.1",
        description="High-intelligence model for complex tasks",
        avg_response_length="Long",
        speed_rating="Medium",
        reasoning_model=False,
    ),
    LLMInfo(
        llm_id="x-ai/grok-4.1-fast:free",
        provider="Grok",
        api_provider="OpenRouter",
        name="grok-4.1-fast",
        description="Fast and efficient model for complex tasks",
        avg_response_length="Medium",
        speed_rating="Fast",
        reasoning_model=True,
    ),
    LLMInfo(
        llm_id="z-ai/glm-4.5-air:free",
        provider="Z.AI",
        api_provider="OpenRouter",
        name="glm-4.5-air",
        description="Z.AI 4.5 Air model",
        avg_response_length="Long",
        speed_rating="Medium",
        reasoning_model=True,
    ),
]

VALID_LLM_IDS = {llm.llm_id for llm in AVAILABLE_LLMS}


def get_llm_info(llm_id: str) -> LLMInfo | None:
    """Get LLM info by ID."""
    for llm in AVAILABLE_LLMS:
        if llm.llm_id == llm_id:
            return llm
    return None
