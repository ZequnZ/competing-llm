
from openai import AsyncAzureOpenAI, DefaultAioHttpClient

from competing_llm.backend.configuration.config import config


def create_async_llm_client():
    """Create an instance of the async Azure OpenAI client.
    This function checks the environment configuration and initializes the client accordingly.
    """

    return AsyncAzureOpenAI(
        api_version=config.azure_openai_api_version,
        azure_endpoint=config.azure_openai_endpoint.get_secret_value(),
        api_key=config.azure_openai_api_key.get_secret_value(),
        http_client=DefaultAioHttpClient(),
    )
