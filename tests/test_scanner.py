"""
Unit tests for core/scanner.py — ScanSession and SecurityScanner.
No live network calls are made; vulnerability tests are mocked.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ─── ScanSession Tests ────────────────────────────────────────────────────────

class TestScanSession:
    """Tests for the ScanSession data class."""

    def setup_method(self):
        from core.scanner import ScanSession
        self.ScanSession = ScanSession

    def _make_result(self, status="VULNERABLE", severity="HIGH"):
        return {
            "test": "Test Name",
            "category": "API1",
            "url": "http://localhost:5000/api/user/1",
            "method": "GET",
            "status": status,
            "severity": severity,
            "description": "Test description",
            "evidence": "HTTP 200 returned for another user's data",
            "recommendation": "Add ownership check"
        }

    def test_init_defaults(self):
        session = self.ScanSession("http://localhost:5000")
        assert session.target_url == "http://localhost:5000"
        assert session.scan_id is not None
        assert session.results == []
        assert session.summary["total_tests"] == 0
        assert session.summary["vulnerabilities_found"] == 0

    def test_custom_scan_id(self):
        session = self.ScanSession("http://localhost:5000", scan_id="custom-123")
        assert session.scan_id == "custom-123"

    def test_add_vulnerable_result_increments_counters(self):
        session = self.ScanSession("http://localhost:5000")
        session.add_results([self._make_result("VULNERABLE", "CRITICAL")])

        assert session.summary["total_tests"] == 1
        assert session.summary["vulnerabilities_found"] == 1
        assert session.summary["critical"] == 1

    def test_add_passed_result(self):
        session = self.ScanSession("http://localhost:5000")
        session.add_results([self._make_result("PASSED", "HIGH")])

        assert session.summary["total_tests"] == 1
        assert session.summary["vulnerabilities_found"] == 0
        assert session.summary["passed"] == 1

    def test_add_info_result(self):
        session = self.ScanSession("http://localhost:5000")
        session.add_results([self._make_result("INFO", "LOW")])

        assert session.summary["info"] == 1
        assert session.summary["vulnerabilities_found"] == 0

    def test_severity_counters_all_levels(self):
        session = self.ScanSession("http://localhost:5000")
        results = [
            self._make_result("VULNERABLE", "CRITICAL"),
            self._make_result("VULNERABLE", "HIGH"),
            self._make_result("VULNERABLE", "MEDIUM"),
            self._make_result("VULNERABLE", "LOW"),
        ]
        session.add_results(results)

        assert session.summary["critical"] == 1
        assert session.summary["high"] == 1
        assert session.summary["medium"] == 1
        assert session.summary["low"] == 1
        assert session.summary["vulnerabilities_found"] == 4

    def test_add_multiple_batches(self):
        session = self.ScanSession("http://localhost:5000")
        session.add_results([self._make_result("VULNERABLE", "HIGH")])
        session.add_results([self._make_result("PASSED", "LOW")])

        assert session.summary["total_tests"] == 2
        assert session.summary["vulnerabilities_found"] == 1
        assert session.summary["passed"] == 1

    def test_finalize_sets_end_time(self):
        session = self.ScanSession("http://localhost:5000")
        assert session.end_time is None
        session.finalize()
        assert session.end_time is not None

    def test_get_duration_before_finalize(self):
        session = self.ScanSession("http://localhost:5000")
        assert session.get_duration() == "In progress"

    def test_get_duration_after_finalize(self):
        session = self.ScanSession("http://localhost:5000")
        session.finalize()
        duration = session.get_duration()
        assert duration.endswith("s")
        assert float(duration[:-1]) >= 0

    def test_to_dict_structure(self):
        session = self.ScanSession("http://localhost:5000", scan_id="test-001")
        session.add_results([self._make_result("VULNERABLE", "HIGH")])
        session.finalize()
        d = session.to_dict()

        assert d["scan_id"] == "test-001"
        assert d["target_url"] == "http://localhost:5000"
        assert "start_time" in d
        assert "end_time" in d
        assert "duration" in d
        assert "summary" in d
        assert "results" in d
        assert len(d["results"]) == 1

    def test_to_dict_is_json_serializable(self):
        session = self.ScanSession("http://localhost:5000")
        session.add_results([self._make_result()])
        session.finalize()
        # Should not raise
        json.dumps(session.to_dict())


# ─── SecurityScanner Tests ────────────────────────────────────────────────────

class TestSecurityScanner:
    """Tests for the SecurityScanner engine."""

    def setup_method(self):
        from core.scanner import SecurityScanner, ScanSession
        self.SecurityScanner = SecurityScanner
        self.ScanSession = ScanSession

    def _make_mock_test_class(self, results=None, raises=False):
        """Create a mock vulnerability test class."""
        mock_instance = MagicMock()
        mock_instance.name = "Mock Test"
        mock_instance.category = "API1"
        mock_instance.severity = "HIGH"

        if raises:
            mock_instance.run.side_effect = Exception("Connection refused")
        else:
            mock_instance.run.return_value = results or []

        mock_cls = MagicMock(return_value=mock_instance)
        return mock_cls

    def test_init_loads_test_classes(self):
        scanner = self.SecurityScanner()
        assert len(scanner.test_classes) > 0

    def test_run_scan_returns_session(self):
        scanner = self.SecurityScanner()
        mock_cls = self._make_mock_test_class(results=[])
        config = {
            "target_url": "http://localhost:5000",
            "headers": {},
            "selected_tests": [mock_cls]
        }
        session = scanner.run_scan(config)
        assert isinstance(session, self.ScanSession)
        assert session.end_time is not None  # finalized

    def test_run_scan_aggregates_results(self):
        scanner = self.SecurityScanner()
        vuln_result = {
            "test": "BOLA Test",
            "category": "API1",
            "url": "http://localhost:5000/api/user/2",
            "method": "GET",
            "status": "VULNERABLE",
            "severity": "CRITICAL",
            "description": "BOLA found",
            "evidence": "Data returned",
            "recommendation": "Add auth check"
        }
        mock_cls = self._make_mock_test_class(results=[vuln_result])
        config = {
            "target_url": "http://localhost:5000",
            "headers": {},
            "selected_tests": [mock_cls]
        }
        session = scanner.run_scan(config)

        assert session.summary["vulnerabilities_found"] == 1
        assert session.summary["critical"] == 1
        assert len(session.results) == 1

    def test_run_scan_handles_test_exception(self):
        scanner = self.SecurityScanner()
        mock_cls = self._make_mock_test_class(raises=True)
        config = {
            "target_url": "http://localhost:5000",
            "headers": {},
            "selected_tests": [mock_cls]
        }
        # Should not raise — errors are caught internally
        session = scanner.run_scan(config)
        assert session is not None

    def test_run_scan_with_multiple_tests(self):
        scanner = self.SecurityScanner()
        vuln = {
            "test": "T", "category": "API1", "url": "http://x", "method": "GET",
            "status": "VULNERABLE", "severity": "HIGH",
            "description": "d", "evidence": "e", "recommendation": "r"
        }
        passed = {**vuln, "status": "PASSED", "severity": "LOW"}

        mock1 = self._make_mock_test_class(results=[vuln])
        mock2 = self._make_mock_test_class(results=[passed])
        config = {
            "target_url": "http://localhost:5000",
            "headers": {},
            "selected_tests": [mock1, mock2]
        }
        session = scanner.run_scan(config)

        assert session.summary["total_tests"] == 2
        assert session.summary["vulnerabilities_found"] == 1
        assert session.summary["passed"] == 1

    def test_save_results_creates_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        scanner = self.SecurityScanner()
        session = self.ScanSession("http://localhost:5000", scan_id="test-save")
        session.finalize()

        filename = scanner.save_results(session, format="json")
        assert (tmp_path / filename).exists()

        with open(tmp_path / filename) as f:
            data = json.load(f)
        assert data["scan_id"] == "test-save"


# ─── ALL_TESTS list validation ────────────────────────────────────────────────

class TestVulnerabilityTestsList:
    """Validates that ALL_TESTS has the expected structure."""

    def test_all_tests_not_empty(self):
        from tests.vulnerability_tests import ALL_TESTS
        assert len(ALL_TESTS) > 0

    def test_all_tests_have_required_attributes(self):
        from tests.vulnerability_tests import ALL_TESTS
        for test_cls in ALL_TESTS:
            instance = test_cls()
            assert hasattr(instance, "name"), f"{test_cls} missing 'name'"
            assert hasattr(instance, "category"), f"{test_cls} missing 'category'"
            assert hasattr(instance, "severity"), f"{test_cls} missing 'severity'"
            assert hasattr(instance, "run"), f"{test_cls} missing 'run'"
            assert callable(instance.run), f"{test_cls}.run is not callable"

    def test_all_tests_severity_valid(self):
        from tests.vulnerability_tests import ALL_TESTS
        valid_severities = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
        for test_cls in ALL_TESTS:
            instance = test_cls()
            assert instance.severity in valid_severities, \
                f"{test_cls} has invalid severity: {instance.severity}"
