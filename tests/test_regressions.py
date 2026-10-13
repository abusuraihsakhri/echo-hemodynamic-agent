"""Integration and boundary regressions for calculator, CLI and API."""
import csv

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from cli import main as calculator_main
from echo_hemodynamic_agent.cli import main as agent_main, parse_csv_bool
from echo_hemodynamics import (
    calculate_lvot_area, calculate_pasp, calculate_bsa,
    classify_ejection_fraction, assess_diastolic_function,
    comprehensive_hemodynamic_assessment,
)


@pytest.mark.parametrize("value,expected", [
    ("False", False), ("false", False), ("0", False),
    ("True", True), ("yes", True), ("1", True), ("", False),
])
def test_csv_boolean_parser(value, expected):
    assert parse_csv_bool(value) is expected


def test_csv_boolean_parser_rejects_ambiguous_value():
    with pytest.raises(ValueError):
        parse_csv_bool("perhaps")


def test_csv_batch_false_flag_not_critical(tmp_path):
    source, output = tmp_path / "source.csv", tmp_path / "out.csv"
    source.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "SYNTH-1,PSEUDO-1,1,1,False,NORMAL\n"
        "SYNTH-2,PSEUDO-2,1,1,True,NORMAL\n", encoding="utf-8",
    )
    assert agent_main(["batch", "-i", str(source), "-o", str(output)]) == 0
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["stat_critical_alerts"] == "0"
    assert rows[1]["stat_critical_alerts"] == "1"


def test_documented_json_flag_after_subcommand(capsys):
    assert calculator_main(["co", "--lvot-diameter", "2", "--lvot-vti", "22", "--hr", "72", "--json"]) == 0
    assert '"co_lpm": 4.98' in capsys.readouterr().out
    assert calculator_main(["--json", "ef", "--ef", "50"]) == 0
    assert '"ef_percent": 50.0' in capsys.readouterr().out


@pytest.mark.parametrize("call", [
    lambda: calculate_lvot_area(float("nan")),
    lambda: calculate_bsa(float("inf"), 70),
    lambda: classify_ejection_fraction(float("nan")),
    lambda: calculate_pasp(2.0, float("-inf")),
    lambda: calculate_pasp(2.0, -1),
    lambda: assess_diastolic_function(80, 60, e_prime=0),
])
def test_invalid_haemodynamic_inputs_raise(call):
    with pytest.raises(ValueError):
        call()


def test_partial_measurements_not_silently_discarded():
    result = comprehensive_hemodynamic_assessment(lvot_diameter_cm=2, lvot_vti_cm=20)
    assert any("Incomplete" in warning for warning in result["warnings"])


def test_diastolic_legacy_warning():
    assert "ASE 2025" in assess_diastolic_function(80, 60, e_prime=10)["clinical_caveat"]


def test_fastapi_serves_local_calculator_and_javascript():
    client = TestClient(app)
    assert "Echo Hemodynamics" in client.get("/").text
    assert "function calculate" in client.get("/calculator.js").text


def test_fastapi_agent_endpoint_still_functions():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "CASE-SYNTH", "target_identifier": "TEST-001",
        "primary_metric": 30, "secondary_metric": 0,
        "status_descriptor": "NOMINAL",
    })
    assert response.status_code == 200
    assert response.json()["total_alerts"] == 1


def test_fastapi_rejects_nonfinite_and_phi_attributes():
    client = TestClient(app)
    payload = {"task_id": "SYNTH-1", "target_identifier": "KEY-1", "primary_metric": 3}
    assert client.post("/api/audit", json={**payload, "primary_metric": "NaN"}).status_code == 422
    response = client.post("/api/audit", json={**payload, "attributes": {"free_text": "MRN: 12345678"}})
    assert response.status_code == 400
    assert "12345678" not in response.text
