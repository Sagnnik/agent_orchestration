from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from app.utils.logger import logger
from app.utils.config import get_settings

PROVIDER_CHAT_MODEL = {
    "ollama": ChatOllama,
    "openai": ChatOpenAI,
    "anthropic": ChatAnthropic,
    "google": ChatGoogleGenerativeAI
}

def get_llm(
    provider: str='openai', 
    model_name: str='gpt-4o-mini', 
    api_key: str | None = None, 
    temperature:float=0.0
) -> BaseChatModel:
    
    settings = get_settings()

    try:
        ModelClass = PROVIDER_CHAT_MODEL[provider]

        if provider == "ollama":
            logger.info(f"[get_llm] Using Ollama model={model_name}")
            return ModelClass(model=model_name, temperature=temperature, num_gpu=1)

        if api_key:
            logger.info(f"[get_llm] Using user-provided API key for provider={provider}")
            return ModelClass(model=model_name, api_key=api_key, temperature=temperature)
        
        if settings.debug:
            provider_key_attr = {
                "openai": "openai_api_key",
                "anthropic": "anthropic_api_key",
                "google": "google_api_key",
            }.get(provider)
            env_key = getattr(settings, provider_key_attr, None) if provider_key_attr else None

            if not env_key:
                logger.error(
                    f"[get_llm] No API key provided and no {provider_key_attr} in .env/settings "
                    f"for provider={provider}"
                )
                raise ValueError(f"No API key configured for provider '{provider}' in debug mode")
            
            logger.info(
                f"[get_llm] Using API key from settings/.env for provider={provider} (debug mode)"
            )
            return ModelClass(model=model_name, api_key=env_key, temperature=temperature)

        logger.error(
            f"[get_llm] Missing API key for provider={provider}"
            "User must supply their own key."
        )
        raise ValueError(
            f"API key must be provided for provider '{provider}' when not in debug mode"
        )
    
    except KeyError:
        logger.error(f"[get_llm] Provider '{provider}' is not recognized.")
        logger.info(f"[get_llm] Available providers: {', '.join(PROVIDER_CHAT_MODEL.keys())}")
        raise

    except Exception as e:
        logger.exception(f"[get_llm] Error initializing LLM for provider='{provider}': {e}")
        raise
    

