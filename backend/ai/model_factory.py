"""
Project TITAN — Model Factory
Creates CAMEL ChatAgent models from the three available API providers:
  - Groq (LLaMA 3.3 70B) — fast reasoning, planning, error analysis
  - Gemini 2.0 Flash — large context, code generation
  - Mistral (via OpenAI-compat endpoint) — documentation, writing
"""

from camel.models import ModelFactory
from camel.types import ModelPlatformType
from backend.config import GROQ_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY


def get_groq_model(model: str = "llama-3.3-70b-versatile"):
    """Fast Groq LLaMA — best for planning, testing, structured JSON output."""
    return ModelFactory.create(
        ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        model_type=model,
        url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
    )


def get_gemini_model(model: str = "gemini-2.0-flash"):
    """Google Gemini — best for long file code generation."""
    return ModelFactory.create(
        ModelPlatformType.GEMINI,
        model_type=model,
    )


def get_mistral_model(model: str = "mistral-small-latest"):
    """Mistral — best for writing, documentation, READMEs."""
    return ModelFactory.create(
        ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        model_type=model,
        url="https://api.mistral.ai/v1",
        api_key=MISTRAL_API_KEY,
    )


# ── Agent → Model Assignments ────────────────────────────────────────────────
# Each agent uses the provider best suited to its task

def planner_model():
    """Groq LLaMA — fast structured JSON output for planning."""
    return get_groq_model("llama-3.3-70b-versatile")


def code_model():
    """Gemini 2.0 Flash — large context, excellent code generation."""
    return get_gemini_model("gemini-2.0-flash")


def testing_model():
    """Groq LLaMA — fast error analysis and diagnosis."""
    return get_groq_model("llama-3.3-70b-versatile")


def docs_model():
    """Mistral — excellent writing quality for documentation and READMEs."""
    return get_mistral_model("mistral-small-latest")


def get_model_by_provider(provider: str):
    """Dynamic router for provider fallback."""
    provider = provider.lower()
    if provider == "groq":
        return get_groq_model()
    elif provider == "gemini":
        return get_gemini_model()
    elif provider == "mistral":
        return get_mistral_model()
    
    # Fallback default
    return get_groq_model()
