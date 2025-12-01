from openai import AsyncAzureOpenAI, AsyncOpenAI, DefaultAioHttpClient

from competing_llm.backend.configuration.config import config


def create_async_llm_client(api_provider: str):
    """Create an instance of the async Azure OpenAI client.
    This function checks the environment configuration and initializes the client accordingly.
    """

    if api_provider == "Azure OpenAI":
        return AsyncAzureOpenAI(
            api_version=config.azure_openai_api_version,
            azure_endpoint=config.azure_openai_endpoint.get_secret_value(),
            api_key=config.azure_openai_api_key.get_secret_value(),
            http_client=DefaultAioHttpClient(),
        )
    elif api_provider == "OpenRouter":
        return AsyncOpenAI(
            base_url=config.openrouter_base_url.get_secret_value(),
            api_key=config.openrouter_api_key.get_secret_value(),
        )
