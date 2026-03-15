"""
Azure OpenAI Service
Centralized wrapper for all Azure OpenAI interactions across agents.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """
    Shared Azure OpenAI client for all agents.

    Provides consistent error handling, retry logic, and JSON output
    across all agent interactions.
    """

    MAX_RETRIES = 3

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        json_output: bool = True,
    ) -> Optional[str]:
        """
        Send a chat completion request with retry logic.

        Args:
            system_prompt: The system role instruction.
            user_prompt: The user message.
            temperature: Sampling temperature (0.2-0.4 for analysis).
            json_output: Whether to enforce JSON response format.

        Returns:
            Response text, or None on failure.

        Raises:
            Exception: If all retries are exhausted.
        """
        kwargs = {
            "model": self.deployment,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        if json_output:
            kwargs["response_format"] = {"type": "json_object"}

        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                logger.warning(f"Azure OpenAI attempt {attempt + 1} failed: {e}")

        raise Exception(f"Azure OpenAI failed after {self.MAX_RETRIES} attempts: {last_error}")

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> Dict:
        """
        Send a chat completion and parse the response as JSON.

        Returns:
            Parsed JSON dict.

        Raises:
            ValueError: If response cannot be parsed as JSON.
        """
        raw = self.complete(system_prompt, user_prompt, temperature, json_output=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}\nRaw: {raw}")
            raise ValueError(f"AI response was not valid JSON: {e}")

    def analyze(self, prompt: str, context: Dict = None, temperature: float = 0.3) -> Dict:
        """
        General-purpose analysis method for agents.

        Args:
            prompt: The analysis question or instruction.
            context: Optional context dict to include in the prompt.
            temperature: Sampling temperature.

        Returns:
            Parsed JSON analysis result.
        """
        user_prompt = prompt
        if context:
            user_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"

        return self.complete_json(
            system_prompt="You are an expert API security analyst. Respond only with valid JSON.",
            user_prompt=user_prompt,
            temperature=temperature,
        )
