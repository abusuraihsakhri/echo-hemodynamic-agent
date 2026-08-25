#!/usr/bin/env python3
"""
Tests for Echocardiography Hemodynamic Calculator.
"""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from echo_hemodynamics import (
    calculate_lvot_area,
    calculate_stroke_volume,
    calculate_stroke_volume_from_diameter,
    calculate_cardiac_output,
    calculate_bsa,
    calculate_cardiac_index,
    classify_ejection_fraction,
    calculate_mva_pressure_half_time,
    classify_mva,
    calculate_pasp,
    classify_pasp,
    assess_diastolic_function,
    comprehensive_hemodynamic_assessment,
)


# =============================================================================
# LVOT Area Tests
# =============================================================================

def test_lvot_area_standard():
    """LVOT diameter 2.0 cm -> area ~3.14 cm^2."""
    area = calculate_lvot_area(2.0)
    expected = math.pi * 1.0 ** 2
    assert abs(area - expected) < 0.01


def test_lvot_area_small():
    """LVOT diameter 1.8 cm."""
    area = calculate_lvot_area(1.8)
    expected = math.pi * 0.9 ** 2
    assert abs(area - expected) < 0.01


def test_lvot_area_large():
    """LVOT diameter 2.5 cm."""
    area = calculate_lvot_area(2.5)
    expected = math.pi * 1.25 ** 2
    assert abs(area - expected) < 0.01


def test_lvot_area_invalid():
    """Zero diameter should raise ValueError."""
    try:
        calculate_lvot_area(0)
        assert False
    except ValueError:
        pass


# =============================================================================
# Stroke Volume Tests
# =============================================================================

def test_stroke_volume_basic():
    """Area 3.0 cm^2, VTI 20 cm -> SV 60 mL."""
    sv = calculate_stroke_volume(3.0, 20.0)
    assert abs(sv - 60.0) < 0.1


def test_stroke_volume_from_diameter():
    """Diameter 2.0 cm, VTI 22 cm -> SV ~69.1 mL."""
    sv = calculate_stroke_volume_from_diameter(2.0, 22.0)
    expected = math.pi * 1.0 ** 2 * 22.0
    assert abs(sv - expected) < 0.1


def test_stroke_volume_invalid():
    """Zero VTI should raise ValueError."""
    try:
        calculate_stroke_volume(3.0, 0)
        assert False
    except ValueError:
        pass


# =============================================================================
# Cardiac Output Tests
# =============================================================================

def test_cardiac_output_basic():
    """SV 70 mL, HR 72 bpm -> CO 5.04 L/min."""
    co = calculate_cardiac_output(70.0, 72.0)
    assert abs(co - 5.04) < 0.01


def test_cardiac_output_high_hr():
    """SV 60 mL, HR 120 bpm -> CO 7.2 L/min."""
    co = calculate_cardiac_output(60.0, 120.0)
    assert abs(co - 7.2) < 0.01


def test_cardiac_output_low():
    """SV 40 mL, HR 60 bpm -> CO 2.4 L/min."""
    co = calculate_cardiac_output(40.0, 60.0)
    assert abs(co - 2.4) < 0.01


# =============================================================================
# BSA Tests
# =============================================================================

def test_bsa_du_bois():
    """Du Bois formula: 170cm, 70kg -> ~1.81 m^2."""
    bsa = calculate_bsa(170, 70, formula="du_bois")
    expected = 0.007184 * (170 ** 0.725) * (70 ** 0.425)
    assert abs(bsa - expected) < 0.01
    assert 1.7 < bsa < 1.9


def test_bsa_mosteller():
    """Mosteller formula: 170cm, 70kg -> ~1.82 m^2."""
    bsa = calculate_bsa(170, 70, formula="mosteller")
    expected = math.sqrt(170 * 70 / 3600)
    assert abs(bsa - expected) < 0.01


def test_bsa_invalid_formula():
    try:
        calculate_bsa(170, 70, formula="unknown")
        assert False
    except ValueError:
        pass


# =============================================================================
# Cardiac Index Tests
# =============================================================================

def test_cardiac_index_normal():
    """CO 5.0, BSA 1.8 -> CI ~2.78."""
    ci = calculate_cardiac_index(5.0, 1.8)
    assert abs(ci - 5.0 / 1.8) < 0.01


def test_cardiac_index_low():
    """CO 3.5, BSA 1.8 -> CI ~1.94 (low)."""
    ci = calculate_cardiac_index(3.5, 1.8)
    assert ci < 2.2


# =============================================================================
# Ejection Fraction Tests
# =============================================================================

def test_ef_normal():
    result = classify_ejection_fraction(60)
    assert result["category"] == "normal"
    assert result["label"] == "Normal LVEF"


def test_ef_hfpef():
    result = classify_ejection_fraction(52)
    assert result["category"] == "hfpef"


def test_ef_hfmref():
    result = classify_ejection_fraction(45)
    assert result["category"] == "hfmrEF"


def test_ef_hfref():
    result = classify_ejection_fraction(30)
    assert result["category"] == "hfref"
    assert result["label"] == "HFrEF"


def test_ef_hyperdynamic():
    result = classify_ejection_fraction(75)
    assert result["category"] == "hyperdynamic"


def test_ef_boundary_55():
    """EF 55% should be normal."""
    result = classify_ejection_fraction(55)
    assert result["category"] == "normal"


def test_ef_boundary_40():
    """EF 40% should be HFmrEF."""
    result = classify_ejection_fraction(40)
    assert result["category"] == "hfmrEF"


def test_ef_boundary_39():
    """EF 39% should be HFrEF."""
    result = classify_ejection_fraction(39)
    assert result["category"] == "hfref"


def test_ef_invalid():
    try:
        classify_ejection_fraction(110)
        assert False
    except ValueError:
        pass


# =============================================================================
# MVA (Pressure Half-Time) Tests
# =============================================================================

def test_mva_normal():
    """PHT 50ms -> MVA 4.4 cm^2 (normal)."""
    mva = calculate_mva_pressure_half_time(50)
    assert abs(mva - 4.4) < 0.1


def test_mva_severe_stenosis():
    """PHT 220ms -> MVA 1.0 cm^2 (severe MS)."""
    mva = calculate_mva_pressure_half_time(220)
    assert abs(mva - 1.0) < 0.01


def test_mva_moderate_stenosis():
    """PHT 147ms -> MVA ~1.5 cm^2."""
    mva = calculate_mva_pressure_half_time(147)
    assert abs(mva - 220.0 / 147) < 0.01


def test_classify_mva_normal():
    result = classify_mva(5.0)
    assert result["severity"] == "normal"


def test_classify_mva_severe():
    result = classify_mva(0.8)
    assert result["severity"] == "severe_stenosis"


# =============================================================================
# PASP Tests
# =============================================================================

def test_pasp_normal():
    """TR velocity 2.0 m/s, RAP 10 -> PASP 26 mmHg."""
    pasp = calculate_pasp(2.0, 10.0)
    assert abs(pasp - 26.0) < 0.1


def test_pasp_elevated():
    """TR velocity 3.5 m/s, RAP 15 -> PASP 64 mmHg."""
    pasp = calculate_pasp(3.5, 15.0)
    expected = 4 * 3.5 ** 2 + 15
    assert abs(pasp - expected) < 0.1


def test_pasp_zero_rap():
    """TR velocity 2.5 m/s, RAP 0 -> PASP 25 mmHg."""
    pasp = calculate_pasp(2.5, 0.0)
    assert abs(pasp - 25.0) < 0.1


def test_classify_pasp_normal():
    result = classify_pasp(25)
    assert result["classification"] == "normal"


def test_classify_pasp_severe():
    result = classify_pasp(65)
    assert result["classification"] == "severe_ph"


# =============================================================================
# Diastolic Function Tests
# =============================================================================

def test_diastolic_normal():
    """E/A 1.33, E/e' 8.0 -> Normal."""
    result = assess_diastolic_function(e_velocity=80, a_velocity=60, e_prime=10)
    assert result["e_a_ratio"] == round(80 / 60, 2)
    assert result["e_e_prime"] == 8.0
    assert result["grade"] == "Normal"


def test_diastolic_grade_I():
    """E/A <0.8 -> Grade I."""
    result = assess_diastolic_function(e_velocity=50, a_velocity=80, e_prime=10)
    assert result["e_a_ratio"] < 0.8
    assert result["grade"] == "Grade I"


def test_diastolic_grade_II():
    """E/A 1.0, E/e' 12 -> Grade II."""
    result = assess_diastolic_function(e_velocity=80, a_velocity=80, e_prime=7)
    assert result["e_e_prime"] > 11
    assert "Grade II" in result["grade"]


def test_diastolic_grade_III():
    """E/A 2.5, E/e' 15 -> Grade III."""
    result = assess_diastolic_function(e_velocity=100, a_velocity=40, e_prime=7)
    assert result["e_a_ratio"] > 2.0
    assert result["e_e_prime"] > 13
    assert "Grade III" in result["grade"]


def test_diastolic_without_eprime():
    """Without e', E/A 1.5 should be indeterminate."""
    result = assess_diastolic_function(e_velocity=90, a_velocity=60)
    assert result["grade"] == "Indeterminate"


def test_diastolic_invalid():
    """Zero velocity should raise ValueError."""
    try:
        assess_diastolic_function(e_velocity=0, a_velocity=60)
        assert False
    except ValueError:
        pass


# =============================================================================
# Comprehensive Assessment Tests
# =============================================================================

def test_comprehensive_basic():
    """Basic comprehensive assessment with CO parameters."""
    result = comprehensive_hemodynamic_assessment(
        lvot_diameter_cm=2.0, lvot_vti_cm=22.0, heart_rate_bpm=72,
    )
    assert "stroke_volume_ml" in result["parameters"]
    assert "cardiac_output_lpm" in result["parameters"]


def test_comprehensive_with_ef():
    """Assessment with reduced EF should generate warning."""
    result = comprehensive_hemodynamic_assessment(ef_percent=30)
    assert len(result["warnings"]) > 0
    assert any("HFrEF" in w for w in result["warnings"])


def test_comprehensive_summary():
    """Summary should be a non-empty string."""
    result = comprehensive_hemodynamic_assessment(ef_percent=60)
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0


# =============================================================================
# CLI Tests
# =============================================================================

def test_cli_co():
    from cli import main
    rc = main(["co", "--lvot-diameter", "2.0", "--lvot-vti", "22", "--hr", "72"])
    assert rc == 0


def test_cli_ef():
    from cli import main
    rc = main(["ef", "--ef", "35"])
    assert rc == 0


def test_cli_mva():
    from cli import main
    rc = main(["mva", "--pht", "220"])
    assert rc == 0


def test_cli_pasp():
    from cli import main
    rc = main(["pasp", "--tr-velocity", "3.0", "--rap", "10"])
    assert rc == 0


def test_cli_diastolic():
    from cli import main
    rc = main(["diastolic", "--e-velocity", "80", "--a-velocity", "60", "--e-prime", "10"])
    assert rc == 0


def test_cli_assess():
    from cli import main
    rc = main(["assess", "--ef", "45", "--pht", "150"])
    assert rc == 0
