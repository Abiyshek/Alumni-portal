"""
GenAI Insight Layer Module
Generates natural language insights using NVIDIA Nemotron via OpenAI API (Streaming).
"""

import os
import logging
import json

log = logging.getLogger("alumni_pipeline")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    log.warning("openai package not installed — GenAI layer will use placeholders")


class GenAIInsightLayer:
    """
    Converts quantitative model outputs into natural language insights using NVIDIA Llama 3.3 70B.
    Uses OpenAI-compatible API endpoint with streaming enabled.

    [SECURITY] The API key is read from an environment variable — never hard-coded.
    """

    SYSTEM_PROMPT = (
        "You are a senior data scientist advising a university alumni relations "
        "team. You have access to ML model outputs from a donor propensity model. "
        "Answer questions clearly and concisely with actionable recommendations. "
        "Cite specific numbers from the provided context when available. "
        "Keep responses under 200 words."
    )

    def __init__(self):
        self.api_key = os.environ.get("NVIDIA_NEMOTRON_API_KEY", "")
        self.base_url = os.environ.get("NVIDIA_API_ENDPOINT", "https://integrate.api.nvidia.com/v1")
        self.model = os.environ.get("NVIDIA_MODEL_NAME", "meta/llama-3.3-70b-instruct")
        self.client = None
        
        if not OPENAI_AVAILABLE:
            log.warning("openai library not installed. Install with: pip install openai")
            return
            
        if not self.api_key:
            log.warning(
                "  NVIDIA_NEMOTRON_API_KEY not set — GenAI layer will return "
                "placeholder responses. Set the env var to enable live insights."
            )
            return
        
        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            log.info(f"✓ NVIDIA Nemotron initialized ({self.model})")
        except Exception as e:
            log.warning(f"Failed to initialize Nemotron client: {e}")

    def ask(self, question: str, context: dict) -> str:
        """Send a question + model context to Nemotron and return the insight (streaming)."""
        if not self.client or not self.api_key:
            log.warning("GenAI API key not configured. Skipping.")
            return ""

        try:
            context_str = json.dumps(context, indent=2, default=str)
            
            # Create completion with streaming enabled
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": (
                            f"MODEL CONTEXT:\n{context_str}\n\n"
                            f"QUESTION: {question}"
                        )
                    }
                ],
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
                stream=True
            )
            
            # Collect streamed response
            full_response = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
            
            return full_response

        except Exception as exc:
            log.error(f"  GenAI API call failed: {exc}")
            return ""

    @staticmethod
    def _placeholder(question: str, context: dict) -> str:
        """Deterministic placeholder when API key is absent."""
        top_feature = context.get("top_feature", "engagement_score")
        ensemble_auc = context.get("ensemble_auc", "N/A")
        return (
            f"[GenAI Placeholder — set NVIDIA_NEMOTRON_API_KEY for live insights]\n"
            f"Based on the model (ensemble AUC={ensemble_auc}), the top driver of donation "
            f"propensity is '{top_feature}'. Alumni with high scores on this metric "
            f"and 7–20 years since graduation represent the highest-value segment. "
            f"Re-engagement campaigns targeting low-engagement, high-salary alumni "
            f"are recommended as the immediate next action."
        )

    def run_insight_queries(self, context: dict) -> None:
        """Run the canonical set of business insight queries."""
        import logging as lg
        
        # Temporarily suppress HTTP request logs
        lg.getLogger("openai").setLevel(lg.WARNING)
        lg.getLogger("httpx").setLevel(lg.WARNING)

        queries = [
            "Which alumni segment is most likely to donate for infrastructure projects?",
            "What engagement behaviors most influence donation probability, and why?",
            "What re-engagement strategy would you recommend for high-salary alumni "
            "with low engagement scores?",
            "Summarise the 3 most actionable findings from this model for the "
            "alumni relations team.",
        ]

        print("\n" + "─" * 60)
        print("  NATURAL LANGUAGE INSIGHTS  (powered by NVIDIA Nemotron)")
        print("─" * 60)
        for q in queries:
            print(f"\n  Q: {q}")
            response = self.ask(q, context)
            print(f"  A: {response}")
            print()



