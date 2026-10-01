"""
Project TITAN — Model Factory
Creates CAMEL ChatAgent models from the three available API providers:
  - Groq (LLaMA 3.3 70B) — fast reasoning, planning, error analysis
  - Gemini 2.0 Flash — large context, code generation
  - Mistral (via OpenAI-compat endpoint) — documentation, writing
"""

from camel.models import ModelFactory
from camel.types import ModelPlatformType

from backend.config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY


def get_groq_model(model: str = "llama-3.3-70b-versatile"):
    """Groq hosted models — fast inference for planning and code tasks."""
    return ModelFactory.create(
        ModelPlatformType.GROQ,
        model_type=model,
        api_key=GROQ_API_KEY,
        timeout=60.0,
        model_config_dict={'max_tokens': 8192},
    )


def get_gemini_model(model: str = "gemini-3.8-flash"):
    """Google Gemini — best for long file code generation."""
    return ModelFactory.create(
        ModelPlatformType.GEMINI,
        model_type=model,
        api_key=GEMINI_API_KEY or None,
        timeout=60.0,
        model_config_dict={'max_tokens': 8192},
    )


def get_mistral_model(model: str = "mistral-small-latest"):
    """Mistral — best for writing, documentation, READMEs."""
    return ModelFactory.create(
        ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        model_type=model,
        url="https://api.mistral.ai/v1",
        api_key=MISTRAL_API_KEY,
        timeout=15.0,
        model_config_dict={'max_tokens': 8192},
    )


# ── Agent → Model Assignments ────────────────────────────────────────────────
# Each agent uses the provider best suited to its task


def planner_model():
    """Gemini 2.0 Flash — fast structured JSON output for planning."""
    return get_gemini_model("gemini-3.8-flash")


def code_model():
    """Gemini 2.0 Flash — large context, excellent for code generation."""
    return get_gemini_model("gemini-3.8-flash")


def testing_model():
    """Gemini 2.0 Flash — fast error analysis and diagnosis."""
    return get_gemini_model("gemini-3.8-flash")


def docs_model():
    """Gemini 2.0 Flash — excellent writing quality for documentation and READMEs."""
    return get_gemini_model("gemini-3.8-flash")


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
