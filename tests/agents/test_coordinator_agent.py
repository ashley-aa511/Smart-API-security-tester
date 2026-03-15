"""
Unit tests for CoordinatorAgent
Tests use mocked Azure OpenAI calls — no real Azure credentials needed.
"""
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ─── Fixtures ────────────────────────────────────────────────────────────────

MOCK_ANALYSIS = {
    "api_type": "REST",
    "auth_method": "None",
    "data_sensitivity": "Medium",
    "domain": "User Management",
    "risk_areas": ["authentication", "authorization", "bola"],
    "reasoning": "Public API with no auth — high risk for unauthorized access"
}

MOCK_SCAN_PLAN = {
    "priority_tests": [
        {
            "test_id": "API2",
            "test_name": "Broken Authentication",
            "priority": "CRITICAL",
            "reason": "No authentication detected",
            "parameters": {"focus_areas": ["token_validation"], "intensity": "high"}
        },
        {
            "test_id": "API1",
            "test_name": "BOLA",
            "priority": "HIGH",
            "reason": "User objects accessible without ownership check",
            "parameters": {"focus_areas": ["object_ids"], "intensity": "medium"}
        }
    ],
    "recommended_order": ["API2", "API5", "API1", "API10", "API8"],
    "estimated_duration_minutes": 12,
    "special_considerations": ["No rate limiting detected"]
}


def _make_mock_response(content: dict) -> MagicMock:
    """Build a mock that looks like an OpenAI chat completion response."""
    msg = MagicMock()
    msg.content = json.dumps(content)
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestCoordinatorAgentInit:
    """Tests for CoordinatorAgent initialization."""

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_init_creates_client(self, mock_azure):
        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()

        mock_azure.assert_called_once_with(
            api_key="test-key",
            api_version="2024-02-15-preview",
            azure_endpoint="https://test.openai.azure.com/"
        )
        assert agent.deployment == "gpt-4o-mini"

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_with_missing_env_vars(self, mock_azure):
        """Agent should still initialize even with missing env vars (fail at call time)."""
        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        assert agent.deployment is None


class TestAnalyzeApi:
    """Tests for CoordinatorAgent.analyze_api()"""

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_analyze_api_returns_dict(self, mock_azure_cls):
        mock_client = MagicMock()
        mock_azure_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_mock_response(MOCK_ANALYSIS)

        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        result = asyncio.run(agent.analyze_api("http://localhost:5000"))

        assert isinstance(result, dict)
        assert result["api_type"] == "REST"
        assert result["auth_method"] == "None"
        assert "risk_areas" in result

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_analyze_api_passes_headers(self, mock_azure_cls):
        mock_client = MagicMock()
        mock_azure_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_mock_response(MOCK_ANALYSIS)

        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        headers = {"Authorization": "Bearer test-token"}
        asyncio.run(agent.analyze_api("http://localhost:5000", headers=headers))

        call_args = mock_client.chat.completions.create.call_args
        # The prompt should include the Authorization header
        user_content = call_args[1]["messages"][1]["content"]
        assert "Authorization" in user_content


class TestCreateScanPlan:
    """Tests for CoordinatorAgent.create_scan_plan()"""

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_create_scan_plan_returns_dict(self, mock_azure_cls):
        mock_client = MagicMock()
        mock_azure_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_mock_response(MOCK_SCAN_PLAN)

        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        result = asyncio.run(agent.create_scan_plan(MOCK_ANALYSIS))

        assert isinstance(result, dict)
        assert "priority_tests" in result
        assert "recommended_order" in result
        assert isinstance(result["priority_tests"], list)
        assert result["estimated_duration_minutes"] == 12

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_create_scan_plan_includes_analysis_context(self, mock_azure_cls):
        mock_client = MagicMock()
        mock_azure_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_mock_response(MOCK_SCAN_PLAN)

        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        asyncio.run(agent.create_scan_plan(MOCK_ANALYSIS))

        call_args = mock_client.chat.completions.create.call_args
        user_content = call_args[1]["messages"][1]["content"]
        assert "Medium" in user_content  # data_sensitivity from MOCK_ANALYSIS


class TestPlanScan:
    """Tests for CoordinatorAgent.plan_scan() — full end-to-end (mocked)."""

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_plan_scan_returns_complete_result(self, mock_azure_cls, capsys):
        mock_client = MagicMock()
        mock_azure_cls.return_value = mock_client
        # First call → analyze_api, second call → create_scan_plan
        mock_client.chat.completions.create.side_effect = [
            _make_mock_response(MOCK_ANALYSIS),
            _make_mock_response(MOCK_SCAN_PLAN),
        ]

        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        result = asyncio.run(agent.plan_scan("http://localhost:5000"))

        assert "api_analysis" in result
        assert "scan_plan" in result
        assert result["target_url"] == "http://localhost:5000"
        assert result["headers"] == {}

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_plan_scan_calls_openai_twice(self, mock_azure_cls):
        mock_client = MagicMock()
        mock_azure_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = [
            _make_mock_response(MOCK_ANALYSIS),
            _make_mock_response(MOCK_SCAN_PLAN),
        ]

        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        asyncio.run(agent.plan_scan("http://localhost:5000"))

        assert mock_client.chat.completions.create.call_count == 2

    @patch("src.agents.coordinator_agent.AzureOpenAI")
    @patch.dict("os.environ", {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini"
    })
    def test_plan_scan_preserves_headers(self, mock_azure_cls):
        mock_client = MagicMock()
        mock_azure_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = [
            _make_mock_response(MOCK_ANALYSIS),
            _make_mock_response(MOCK_SCAN_PLAN),
        ]

        from src.agents.coordinator_agent import CoordinatorAgent
        agent = CoordinatorAgent()
        headers = {"Authorization": "Bearer abc123"}
        result = asyncio.run(agent.plan_scan("http://localhost:5000", headers=headers))

        assert result["headers"] == headers
