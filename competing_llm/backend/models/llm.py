from datetime import datetime

from pydantic import BaseModel, Field, validator


class ChatRequest(BaseModel):
    """Request model for chat streaming."""

    prompt: str = Field(
        ..., description="User's input prompt", min_length=1, max_length=1000
    )
    llm_id: int = Field(..., description="LLM model identifier", ge=1, le=5)
    delay: float | None = Field(
        0.05, description="Delay between chunks in seconds", gt=0, le=1.0
    )

    @validator("prompt")
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or just whitespace")
        return v.strip()


class BatchChatRequest(BaseModel):
    """Request model for batch chat streaming from multiple LLMs."""

    prompt: str = Field(
        ...,
        description="User's input prompt",
        min_length=1,
        max_length=1000,
        examples=["What is the capital of France?"],
    )
    llm_ids: list[int] = Field(
        ...,
        description="List of LLM model identifiers",
        min_items=1,
        max_items=5,
        examples=[[1, 2, 3]],
    )
    delay: float | None = Field(
        0.05,
        description="Delay between chunks in seconds",
        gt=0,
        le=1.0,
        examples=[0.05],
    )

    @validator("prompt")
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or just whitespace")
        return v.strip()

    @validator("llm_ids")
    def validate_llm_ids(cls, v):
        if not v:
            raise ValueError("At least one LLM ID must be provided")

        for llm_id in v:
            if llm_id < 1 or llm_id > 5:
                raise ValueError(f"Invalid LLM ID: {llm_id}. Must be between 1 and 5")

        if len(set(v)) != len(v):
            raise ValueError("Duplicate LLM IDs are not allowed")

        return v


class StreamChunk(BaseModel):
    """SSE chunk format for streaming responses."""

    chunk_id: int = Field(..., description="Sequential chunk identifier")
    text: str = Field(..., description="Text content of this chunk")
    timestamp: str = Field(..., description="ISO 8601 timestamp of chunk generation")
    llm_id: int = Field(..., description="Source LLM model identifier")
    is_complete: bool = Field(False, description="Whether this is the final chunk")
    source_llm: int | None = Field(
        None, description="For batch requests, indicates source LLM"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""

    llm_id: int = Field(..., description="LLM model identifier")
    prompt: str = Field(..., description="Original prompt")
    content: str = Field(..., description="Generated content")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class BatchChatResponse(BaseModel):
    """Response model for batch non-streaming chat."""

    responses: list[ChatResponse] = Field(..., description="List of chat responses")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class ErrorResponse(BaseModel):
    """Error response format."""

    error: str = Field(..., description="Error type/classification")
    message: str = Field(..., description="Human-readable error message")
    timestamp: str = Field(..., description="ISO 8601 timestamp of error occurrence")
    llm_id: int | None = Field(
        None, description="LLM ID that caused the error, if applicable"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    available_llms: list[int] = Field(..., description="List of available LLM IDs")
    version: str = Field("1.0.0", description="API version")


class LLMInfo(BaseModel):
    """Information about a specific LLM."""

    llm_id: int = Field(..., description="LLM model identifier")
    name: str = Field(..., description="Human-readable LLM name")
    description: str = Field(..., description="LLM description and capabilities")
    avg_response_length: str = Field(..., description="Typical response length range")
    speed_rating: str = Field(
        ..., description="Speed classification (Fast/Medium/Slow)"
    )


class LLMListResponse(BaseModel):
    """Response containing information about all available LLMs."""

    llms: list[LLMInfo] = Field(..., description="List of available LLMs")
    total_count: int = Field(..., description="Total number of available LLMs")
