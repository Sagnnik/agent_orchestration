from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv

load_dotenv()   # This is for dev only

PROVIDER_CHAT_MODEL = {
    "ollama": ChatOllama,
    "openai": ChatOpenAI,
    "anthropic": ChatAnthropic,
    "google": ChatGoogleGenerativeAI
}

def get_llm(provider: str, model_name: str, api_key: str = None, temperature:int=0) -> BaseChatModel:
    try:
        ModelClass = PROVIDER_CHAT_MODEL[provider]
        if provider == "ollama":
            model = ModelClass(model=model_name, temperature=temperature, num_gpu=1)
        else:
            if not api_key:
                 print(f"API Key is missing for provider '{provider}'")
            model = ModelClass(model=model_name, api_key=api_key, temperature=temperature)
        
        return model
    
    except KeyError:
        print(f"Error: Provider '{provider}' is not recognized.")
        print(f"Available providers are: {', '.join(PROVIDER_CHAT_MODEL.keys())}")
        return None
 
    except Exception as e:
        print(f"Error occurred while initializing the LLM for provider '{provider}': {e}")
        return None
    

