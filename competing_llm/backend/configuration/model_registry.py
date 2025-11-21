from competing_llm.backend.models.schema import LLMInfo

# Define available LLMs
AVAILABLE_LLMS = [
    LLMInfo(
        llm_id="gpt-5-nano",
        provider="Azure OpenAI",
        name="GPT-5 Nano",
        description="Next-gen efficient model with reasoning capabilities",
        avg_response_length="Medium",
        speed_rating="Fast",
        reasoning_model=True,
    ),
    LLMInfo(
        llm_id="gpt-4.1",
        provider="Azure OpenAI",
        name="GPT-4.1",
        description="High-intelligence model for complex tasks",
        avg_response_length="Long",
        speed_rating="Medium",
        reasoning_model=False,
    ),
]

VALID_LLM_IDS = {llm.llm_id for llm in AVAILABLE_LLMS}

def get_llm_info(llm_id: str) -> LLMInfo | None:
    """Get LLM info by ID."""
    for llm in AVAILABLE_LLMS:
        if llm.llm_id == llm_id:
            return llm
    return None

