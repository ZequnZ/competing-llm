from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class LLMInfo(BaseModel):
    """Information about a specific LLM."""

    llm_id: str = Field(..., description="LLM model identifier (e.g., 'gpt-4.1')")
    provider: str = Field(..., description="LLM provider (e.g., 'Azure OpenAI')")
    name: str = Field(..., description="Human-readable LLM name")
    description: str = Field(..., description="LLM description and capabilities")
    avg_response_length: str = Field(..., description="Typical response length range")
    reasoning_model: bool = Field(
        default=False, description="Whether the model is a reasoning model"
    )
    speed_rating: str = Field(
        ..., description="Speed classification (Fast/Medium/Slow)"
    )
    reasoning_model: bool = Field(
        False, description="Whether this is a reasoning model"
    )


class LLMListResponse(BaseModel):
    """Response containing information about all available LLMs."""

    llms: List[LLMInfo] = Field(..., description="List of available LLMs")
    total_count: int = Field(..., description="Total number of available LLMs")


class ChatRequest(BaseModel):
    """Request model for single chat completion."""

    prompt: str = Field(
        ..., description="User's input prompt", min_length=1
    )
    llm_id: str = Field(..., description="LLM model identifier")
    
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or just whitespace")
        return v.strip()


class BatchChatRequest(BaseModel):
    """Request model for batch chat completions."""

    prompt: str = Field(
        ..., description="User's input prompt", min_length=1
    )
    llm_ids: List[str] = Field(
        ..., description="List of LLM model identifiers", min_items=1
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or just whitespace")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat completion."""

    llm_id: str = Field(..., description="LLM model identifier")
    content: str = Field(..., description="Generated content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")


class BatchChatResponse(BaseModel):
    """Response model for batch chat completions."""

    responses: List[ChatResponse] = Field(..., description="List of chat responses")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
