"""
Security-focused tests for echo-hemodynamic-agent.
Tests PHI guard, audit trail integrity, and input validation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import (
    PHIGuard,
    AuditTrail,
    AuditLogger,
    SecurityException,
    assert_no_phi,
)
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor


class TestPHIGuard:
    """Tests for PHI detection and redaction."""

    def test_mrn_detection(self):
        """MRN patterns should be detected."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("MRN: 994827")

    def test_ssn_detection(self):
        """SSN patterns should be detected."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phone_detection(self):
        """Phone number patterns should be detected."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_email_detection(self):
        """Email patterns should be detected."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@hospital.com")

    def test_doe_detection(self):
        """Common placeholder names should be detected."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient John Doe admitted")

    def test_clean_text_passes(self):
        """Non-PHI text should pass without exception."""
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Blood pressure 120/80 mmHg")
        PHIGuard.assert_no_phi("")

    def test_redact_phi(self):
        """PHI should be redacted from text."""
        redacted = PHIGuard.redact_phi("Patient MRN-12345678 and SSN 123-45-6789")
        assert "MRN" not in redacted or "[REDACTED_IDENTIFIER]" in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted

    def test_none_input_safe(self):
        """None/empty input should not raise."""
        PHIGuard.assert_no_phi("")
        assert_no_phi("")


class TestAuditTrail:
    """Tests for HMAC-SHA256 audit trail integrity."""

    def test_audit_trail_creation(self):
        """Audit trail should be created with a secret key."""
        trail = AuditTrail(secret_key="test-secret-key")
        assert len(trail.get_trail()) == 0

    def test_audit_logging(self):
        """Logging should create entries with hashes."""
        trail = AuditTrail(secret_key="test-secret-key")
        entry = trail.log("test_actor", "tier1", "TEST_EVENT", {"data": "value"})
        assert "audit_id" in entry
        assert "current_hash" in entry
        assert "prev_hash" in entry
        assert len(trail.get_trail()) == 1

    def test_audit_chain_integrity(self):
        """Audit chain should maintain integrity across multiple entries."""
        trail = AuditTrail(secret_key="test-secret-key")
        trail.log("actor1", "tier1", "EVENT_1", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_2", {"data": "value2"})
        trail.log("actor3", "tier1", "EVENT_3", {"data": "value3"})
        assert trail.verify_integrity() is True

    def test_audit_tamper_detection(self):
        """Tampered entries should fail integrity check."""
        trail = AuditTrail(secret_key="test-secret-key")
        trail.log("actor1", "tier1", "EVENT_1", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_2", {"data": "value2"})
        # Tamper with the first entry
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False

    def test_audit_with_env_key(self):
        """Audit trail should work with environment variable key."""
        import os
        os.environ["AUDIT_SECRET_KEY"] = "env-based-key"
        trail = AuditTrail()
        trail.log("actor", "tier", "EVENT", {"data": "value"})
        assert trail.verify_integrity() is True
        del os.environ["AUDIT_SECRET_KEY"]

    def test_phi_blocked_in_audit(self):
        """PHI in audit details should raise SecurityException."""
        trail = AuditTrail(secret_key="test-secret-key")
        with pytest.raises(SecurityException):
            trail.log("actor", "tier", "EVENT", {"note": "Patient MRN-12345678"})


class TestInputValidation:
    """Tests for input validation in calculations."""

    def test_negative_lvot_diameter(self):
        """Negative LVOT diameter should raise ValueError."""
        from echo_hemodynamics import calculate_lvot_area
        with pytest.raises(ValueError):
            calculate_lvot_area(-1.0)

    def test_zero_heart_rate(self):
        """Zero heart rate should raise ValueError."""
        from echo_hemodynamics import calculate_cardiac_output
        with pytest.raises(ValueError):
            calculate_cardiac_output(70.0, 0.0)

    def test_negative_tr_velocity(self):
        """Negative TR velocity should raise ValueError."""
        from echo_hemodynamics import calculate_pasp
        with pytest.raises(ValueError):
            calculate_pasp(-2.0, 10.0)

    def test_invalid_ef_range(self):
        """EF outside 0-100 should raise ValueError."""
        from echo_hemodynamics import classify_ejection_fraction
        with pytest.raises(ValueError):
            classify_ejection_fraction(150.0)
        with pytest.raises(ValueError):
            classify_ejection_fraction(-10.0)

    def test_invalid_bsa_formula(self):
        """Unknown BSA formula should raise ValueError."""
        from echo_hemodynamics import calculate_bsa
        with pytest.raises(ValueError):
            calculate_bsa(170, 70, formula="invalid")


class TestSupervisorSecurity:
    """Tests for supervisor security features."""

    def test_supervisor_blocks_phi_in_task_id(self):
        """Supervisor should block PHI in task_id."""
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="Patient MRN-12345678",
            target_identifier="KEY-01",
            primary_metric=10.0,
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)

    def test_supervisor_blocks_phi_in_target(self):
        """Supervisor should block PHI in target_identifier."""
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="TASK-01",
            target_identifier="SSN 123-45-6789",
            primary_metric=10.0,
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)

    def test_supervisor_blocks_phi_in_descriptor(self):
        """Supervisor should block PHI in status_descriptor."""
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="TASK-01",
            target_identifier="KEY-01",
            primary_metric=10.0,
            status_descriptor="Patient John Doe",
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)
