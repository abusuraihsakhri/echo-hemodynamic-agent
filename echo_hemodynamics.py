#!/usr/bin/env python3
"""
Echocardiography Hemodynamic Calculator

Real clinical calculations for echocardiography hemodynamics including:
- Cardiac Output (CO) = Stroke Volume x Heart Rate
- Stroke Volume (SV) = LVOT area x LVOT VTI
- Cardiac Index (CI) = CO / BSA
- Ejection Fraction (EF) classification
- Mitral valve area (Pressure Half-Time method)
- Pulmonary artery systolic pressure (PASP)
- Diastolic function grading (E/A, E/e')

References:
- ASE Guidelines for Echocardiography
- Nagueh SF et al. Recommendations for Evaluation of LV Diastolic Function (ASE/EACVI 2016)
- Baumgartner H et al. Echocardiographic Assessment of Valve Stenosis (ASE/EACVI 2017)

Author: Medical Calculator Project
License: MIT
"""

import math
from typing import Dict, Any, Optional


# =============================================================================
# EJECTION FRACTION CLASSIFICATION
# =============================================================================

EF_CATEGORIES = {
    "normal": {"min": 55, "max": 70, "label": "Normal LVEF", "description": "Normal left ventricular systolic function"},
    "hfmrEF": {"min": 40, "max": 49, "label": "HFmrEF", "description": "Heart failure with mildly reduced ejection fraction (40-49%)"},
    "hfref": {"min": 0, "max": 39, "label": "HFrEF", "description": "Heart failure with reduced ejection fraction (<40%)"},
    "hfpef": {"min": 50, "max": 100, "label": "HFpEF", "description": "Heart failure with preserved ejection fraction (>=50%)"},
    "hyperdynamic": {"min": 70, "max": 100, "label": "Hyperdynamic", "description": "Hyperdynamic LVEF (>70%); consider sepsis, anemia, thyrotoxicosis"},
}


# =============================================================================
# DIASTOLIC FUNCTION GRADING (ASE/EACVI 2016)
# =============================================================================

DIASTOLIC_GRADES = {
    "normal": {
        "grade": "Normal",
        "e_a_ratio": (0.8, 2.0),
        "e_e_prime": (0, 8),
        "description": "Normal diastolic function",
        "la_pressure": "Normal",
    },
    "grade_I": {
        "grade": "Grade I",
        "e_a_ratio": (0.0, 0.8),
        "e_e_prime": (0, 8),
        "description": "Impaired relaxation (mild diastolic dysfunction)",
        "la_pressure": "Normal",
    },
    "grade_II": {
        "grade": "Grade II",
        "e_a_ratio": (0.8, 2.0),
        "e_e_prime": (9, 12),
        "description": "Pseudonormal filling pattern (moderate diastolic dysfunction)",
        "la_pressure": "Elevated",
    },
    "grade_III": {
        "grade": "Grade III",
        "e_a_ratio": (2.0, 99.0),
        "e_e_prime": (13, 99),
        "description": "Restrictive filling pattern (severe diastolic dysfunction)",
        "la_pressure": "Markedly elevated",
    },
}


# =============================================================================
# CORE CALCULATION FUNCTIONS
# =============================================================================

def calculate_lvot_area(lvot_diameter_cm: float) -> float:
    """
    Calculate LVOT (Left Ventricular Outflow Tract) cross-sectional area.
    
    Area = pi x (diameter/2)^2
    
    Args:
        lvot_diameter_cm: LVOT diameter in centimeters (typically 2.0-2.5 cm)
    
    Returns:
        LVOT area in cm^2
    """
    if lvot_diameter_cm <= 0:
        raise ValueError("LVOT diameter must be positive")
    return math.pi * (lvot_diameter_cm / 2.0) ** 2


def calculate_stroke_volume(lvot_area_cm2: float, lvot_vti_cm: float) -> float:
    """
    Calculate Stroke Volume from LVOT measurements.
    
    SV = LVOT area x LVOT VTI
    
    The VTI (Velocity Time Integral) is obtained by tracing the spectral
    Doppler envelope of flow through the LVOT.
    
    Args:
        lvot_area_cm2: LVOT cross-sectional area in cm^2
        lvot_vti_cm: LVOT VTI in cm (from pulsed-wave Doppler)
    
    Returns:
        Stroke volume in mL (cm^3)
    """
    if lvot_area_cm2 <= 0:
        raise ValueError("LVOT area must be positive")
    if lvot_vti_cm <= 0:
        raise ValueError("LVOT VTI must be positive")
    return lvot_area_cm2 * lvot_vti_cm


def calculate_stroke_volume_from_diameter(lvot_diameter_cm: float, lvot_vti_cm: float) -> float:
    """
    Calculate Stroke Volume directly from LVOT diameter and VTI.
    
    SV = pi x (d/2)^2 x VTI
    
    Args:
        lvot_diameter_cm: LVOT diameter in cm
        lvot_vti_cm: LVOT VTI in cm
    
    Returns:
        Stroke volume in mL
    """
    area = calculate_lvot_area(lvot_diameter_cm)
    return calculate_stroke_volume(area, lvot_vti_cm)


def calculate_cardiac_output(stroke_volume_ml: float, heart_rate_bpm: float) -> float:
    """
    Calculate Cardiac Output.
    
    CO = SV x HR
    
    Args:
        stroke_volume_ml: Stroke volume in mL
        heart_rate_bpm: Heart rate in beats per minute
    
    Returns:
        Cardiac output in L/min
    """
    if stroke_volume_ml <= 0:
        raise ValueError("Stroke volume must be positive")
    if heart_rate_bpm <= 0:
        raise ValueError("Heart rate must be positive")
    return (stroke_volume_ml * heart_rate_bpm) / 1000.0


def calculate_bsa(height_cm: float, weight_kg: float, formula: str = "du_bois") -> float:
    """
    Calculate Body Surface Area.
    
    Du Bois formula: BSA = 0.007184 x height^0.725 x weight^0.425
    Mosteller formula: BSA = sqrt((height x weight) / 3600)
    
    Args:
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        formula: "du_bois" (default) or "mosteller"
    
    Returns:
        BSA in m^2
    """
    if height_cm <= 0:
        raise ValueError("Height must be positive")
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    
    if formula == "du_bois":
        return 0.007184 * (height_cm ** 0.725) * (weight_kg ** 0.425)
    elif formula == "mosteller":
        return math.sqrt((height_cm * weight_kg) / 3600.0)
    else:
        raise ValueError(f"Unknown BSA formula: {formula}. Use 'du_bois' or 'mosteller'")


def calculate_cardiac_index(cardiac_output_lpm: float, bsa_m2: float) -> float:
    """
    Calculate Cardiac Index.
    
    CI = CO / BSA
    
    Normal CI: 2.5-4.0 L/min/m^2
    
    Args:
        cardiac_output_lpm: Cardiac output in L/min
        bsa_m2: Body surface area in m^2
    
    Returns:
        Cardiac index in L/min/m^2
    """
    if bsa_m2 <= 0:
        raise ValueError("BSA must be positive")
    if cardiac_output_lpm < 0:
        raise ValueError("Cardiac output cannot be negative")
    return cardiac_output_lpm / bsa_m2


def classify_ejection_fraction(ef_percent: float) -> Dict[str, Any]:
    """
    Classify ejection fraction per ACC/AHA guidelines.
    
    Normal: >=55%
    HFpEF: >=50% (with HF symptoms)
    HFmrEF: 40-49%
    HFrEF: <40%
    
    Args:
        ef_percent: Ejection fraction as percentage (0-100)
    
    Returns:
        Dictionary with EF classification
    """
    if ef_percent < 0 or ef_percent > 100:
        raise ValueError("EF must be between 0 and 100")

    if ef_percent >= 70:
        category = "hyperdynamic"
    elif ef_percent >= 55:
        category = "normal"
    elif ef_percent >= 50:
        category = "hfpef"
    elif ef_percent >= 40:
        category = "hfmrEF"
    else:
        category = "hfref"

    cat_info = EF_CATEGORIES[category]
    return {
        "ef_percent": ef_percent,
        "category": category,
        "label": cat_info["label"],
        "description": cat_info["description"],
    }


def calculate_mva_pressure_half_time(pht_ms: float) -> float:
    """
    Calculate Mitral Valve Area using the Pressure Half-Time method.
    
    MVA = 220 / PHT
    
    The pressure half-time is the time for the peak transmitral pressure
    gradient to decrease by half. Measured from the deceleration slope of
    the E-wave on mitral inflow Doppler.
    
    Normal MVA: 4-6 cm^2
    Mitral stenosis: MVA < 2.0 cm^2 (severe < 1.0 cm^2)
    
    Args:
        pht_ms: Pressure half-time in milliseconds
    
    Returns:
        Mitral valve area in cm^2
    """
    if pht_ms <= 0:
        raise ValueError("Pressure half-time must be positive")
    return 220.0 / pht_ms


def classify_mva(mva_cm2: float) -> Dict[str, Any]:
    """
    Classify mitral valve area severity.
    
    Args:
        mva_cm2: Mitral valve area in cm^2
    
    Returns:
        Dictionary with severity classification
    """
    if mva_cm2 >= 4.0:
        severity = "normal"
        description = "Normal mitral valve area"
    elif mva_cm2 >= 2.0:
        severity = "mild_stenosis"
        description = "Mild mitral stenosis"
    elif mva_cm2 >= 1.5:
        severity = "moderate_stenosis"
        description = "Moderate mitral stenosis"
    elif mva_cm2 >= 1.0:
        severity = "moderate_severe_stenosis"
        description = "Moderate-severe mitral stenosis"
    else:
        severity = "severe_stenosis"
        description = "Severe mitral stenosis"

    return {
        "mva_cm2": round(mva_cm2, 2),
        "severity": severity,
        "description": description,
    }


def calculate_pasp(tr_velocity_ms: float, rap_mmhg: float = 10.0) -> float:
    """
    Calculate Pulmonary Artery Systolic Pressure.
    
    PASP = 4 x (TR velocity)^2 + RAP
    
    TR velocity is obtained from the tricuspid regurgitation jet
    using continuous-wave Doppler.
    
    Normal PASP: 15-30 mmHg
    Pulmonary hypertension: PASP > 35-40 mmHg (estimated)
    
    Args:
        tr_velocity_ms: Tricuspid regurgitation peak velocity in m/s
        rap_mmhg: Right atrial pressure in mmHg (default 10 mmHg)
    
    Returns:
        PASP in mmHg
    """
    if tr_velocity_ms < 0:
        raise ValueError("TR velocity cannot be negative")
    return 4.0 * (tr_velocity_ms ** 2) + rap_mmhg


def classify_pasp(pasp_mmhg: float) -> Dict[str, Any]:
    """
    Classify pulmonary artery systolic pressure.
    
    Args:
        pasp_mmhg: PASP in mmHg
    
    Returns:
        Dictionary with classification
    """
    if pasp_mmhg <= 30:
        classification = "normal"
        description = "Normal PASP"
    elif pasp_mmhg <= 40:
        classification = "borderline"
        description = "Borderline elevated PASP"
    elif pasp_mmhg <= 50:
        classification = "mild_ph"
        description = "Mildly elevated - possible pulmonary hypertension"
    elif pasp_mmhg <= 60:
        classification = "moderate_ph"
        description = "Moderately elevated - likely pulmonary hypertension"
    else:
        classification = "severe_ph"
        description = "Severely elevated - significant pulmonary hypertension"

    return {
        "pasp_mmhg": round(pasp_mmhg, 1),
        "classification": classification,
        "description": description,
    }


def assess_diastolic_function(
    e_velocity: float,
    a_velocity: float,
    e_prime: Optional[float] = None,
    la_volume_index: Optional[float] = None,
    tr_velocity: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Assess diastolic function per ASE/EACVI 2016 guidelines.
    
    Parameters:
    - E/A ratio: mitral E-wave / A-wave velocity ratio
    - E/e' ratio: mitral E-wave / tissue Doppler e' velocity
    - LA volume index (optional): indexed LA volume in mL/m^2
    - TR velocity (optional): tricuspid regurgitation velocity in m/s
    
    Grading:
    - Normal: E/A 0.8-2.0, E/e' <8
    - Grade I (impaired relaxation): E/A <0.8
    - Grade II (pseudonormal): E/A 0.8-2.0, E/e' 9-12
    - Grade III (restrictive): E/A >2.0, E/e' >13
    
    Args:
        e_velocity: Mitral E-wave velocity (cm/s)
        a_velocity: Mitral A-wave velocity (cm/s)
        e_prime: Tissue Doppler e' velocity (cm/s), medial or averaged
        la_volume_index: Left atrial volume index (mL/m^2)
        tr_velocity: TR peak velocity (m/s)
    
    Returns:
        Dictionary with diastolic function assessment
    """
    if e_velocity <= 0 or a_velocity <= 0:
        raise ValueError("E and A velocities must be positive")

    e_a_ratio = e_velocity / a_velocity
    result = {
        "e_velocity": e_velocity,
        "a_velocity": a_velocity,
        "e_a_ratio": round(e_a_ratio, 2),
    }

    e_e_prime = None
    if e_prime is not None and e_prime > 0:
        e_e_prime = round(e_velocity / e_prime, 1)
        result["e_prime"] = e_prime
        result["e_e_prime"] = e_e_prime

    if la_volume_index is not None:
        result["la_volume_index"] = la_volume_index
        result["la_enlarged"] = la_volume_index > 34  # >34 mL/m^2 is enlarged

    if tr_velocity is not None:
        result["tr_velocity"] = tr_velocity

    # Grade diastolic function
    grade = _grade_diastolic(e_a_ratio, e_e_prime, la_volume_index, tr_velocity)
    result.update(grade)

    return result


def _grade_diastolic(
    e_a_ratio: float,
    e_e_prime: Optional[float],
    la_volume_index: Optional[float],
    tr_velocity: Optional[float],
) -> Dict[str, Any]:
    """Internal function to grade diastolic function."""
    
    # Grade I: Impaired relaxation - E/A < 0.8
    if e_a_ratio < 0.8:
        return {
            "grade": "Grade I",
            "grade_label": "Impaired relaxation",
            "description": "Mild diastolic dysfunction. LA pressure typically normal.",
            "la_pressure_estimate": "Normal",
        }

    # Grade III: Restrictive - E/A > 2.0 (and E/e' > 13 if available)
    if e_a_ratio > 2.0:
        if e_e_prime is not None and e_e_prime > 13:
            return {
                "grade": "Grade III",
                "grade_label": "Restrictive filling",
                "description": "Severe diastolic dysfunction. LA pressure markedly elevated.",
                "la_pressure_estimate": "Markedly elevated",
            }
        elif e_e_prime is None:
            return {
                "grade": "Grade III (probable)",
                "grade_label": "Restrictive filling pattern",
                "description": "E/A >2.0 suggests restrictive filling. Confirm with E/e'.",
                "la_pressure_estimate": "Likely elevated",
            }

    # Grade II: Pseudonormal - E/A 0.8-2.0 with elevated E/e'
    if 0.8 <= e_a_ratio <= 2.0:
        if e_e_prime is not None:
            if e_e_prime > 13:
                return {
                    "grade": "Grade II",
                    "grade_label": "Pseudonormal (moderate)",
                    "description": "Moderate diastolic dysfunction. Pseudonormal filling pattern with elevated LA pressure.",
                    "la_pressure_estimate": "Elevated",
                }
            elif 9 <= e_e_prime <= 12:
                return {
                    "grade": "Grade II",
                    "grade_label": "Pseudonormal (borderline)",
                    "description": "Borderline diastolic dysfunction. May need additional parameters.",
                    "la_pressure_estimate": "Borderline elevated",
                }
            else:  # E/e' < 8
                return {
                    "grade": "Normal",
                    "grade_label": "Normal diastolic function",
                    "description": "Normal diastolic function. E/A and E/e' within normal limits.",
                    "la_pressure_estimate": "Normal",
                }
        else:
            # Without E/e', can't distinguish normal from pseudonormal
            return {
                "grade": "Indeterminate",
                "grade_label": "E/A 0.8-2.0 without E/e'",
                "description": "Cannot distinguish normal from pseudonormal without E/e' ratio. Additional parameters needed.",
                "la_pressure_estimate": "Indeterminate",
            }

    return {
        "grade": "Indeterminate",
        "grade_label": "Unable to classify",
        "description": "Insufficient data for diastolic grading.",
        "la_pressure_estimate": "Indeterminate",
    }


def comprehensive_hemodynamic_assessment(
    lvot_diameter_cm: Optional[float] = None,
    lvot_vti_cm: Optional[float] = None,
    heart_rate_bpm: Optional[float] = None,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    ef_percent: Optional[float] = None,
    pht_ms: Optional[float] = None,
    tr_velocity_ms: Optional[float] = None,
    rap_mmhg: float = 10.0,
    e_velocity: Optional[float] = None,
    a_velocity: Optional[float] = None,
    e_prime: Optional[float] = None,
    la_volume_index: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Comprehensive echocardiographic hemodynamic assessment.
    
    Args:
        lvot_diameter_cm: LVOT diameter in cm
        lvot_vti_cm: LVOT VTI in cm
        heart_rate_bpm: Heart rate in bpm
        height_cm: Patient height in cm
        weight_kg: Patient weight in kg
        ef_percent: Ejection fraction in %
        pht_ms: Pressure half-time in ms
        tr_velocity_ms: TR velocity in m/s
        rap_mmhg: Right atrial pressure in mmHg
        e_velocity: Mitral E-wave velocity
        a_velocity: Mitral A-wave velocity
        e_prime: Tissue Doppler e' velocity
        la_volume_index: LA volume index in mL/m^2
    
    Returns:
        Comprehensive assessment dictionary
    """
    result = {"parameters": {}, "findings": [], "warnings": []}

    # Cardiac output/index
    if lvot_diameter_cm and lvot_vti_cm and heart_rate_bpm:
        sv = calculate_stroke_volume_from_diameter(lvot_diameter_cm, lvot_vti_cm)
        co = calculate_cardiac_output(sv, heart_rate_bpm)
        result["parameters"]["stroke_volume_ml"] = round(sv, 1)
        result["parameters"]["cardiac_output_lpm"] = round(co, 2)

        if height_cm and weight_kg:
            bsa = calculate_bsa(height_cm, weight_kg)
            ci = calculate_cardiac_index(co, bsa)
            result["parameters"]["bsa_m2"] = round(bsa, 2)
            result["parameters"]["cardiac_index"] = round(ci, 2)
            if ci < 2.2:
                result["warnings"].append(f"Low cardiac index ({ci:.2f} L/min/m^2) - possible low output state")

    # EF classification
    if ef_percent is not None:
        ef_result = classify_ejection_fraction(ef_percent)
        result["parameters"]["ejection_fraction"] = ef_result
        if ef_percent < 40:
            result["warnings"].append(f"Reduced EF ({ef_percent}%) - HFrEF")
            result["findings"].append(ef_result["description"])

    # MVA from PHT
    if pht_ms is not None:
        mva = calculate_mva_pressure_half_time(pht_ms)
        mva_class = classify_mva(mva)
        result["parameters"]["mitral_valve_area"] = mva_class
        if mva < 2.0:
            result["warnings"].append(f"Mitral stenosis: MVA {mva:.2f} cm^2 ({mva_class['severity']})")
            result["findings"].append(mva_class["description"])

    # PASP
    if tr_velocity_ms is not None:
        pasp = calculate_pasp(tr_velocity_ms, rap_mmhg)
        pasp_class = classify_pasp(pasp)
        result["parameters"]["pasp"] = pasp_class
        if pasp > 40:
            result["warnings"].append(f"Elevated PASP ({pasp:.1f} mmHg) - {pasp_class['description']}")
            result["findings"].append(pasp_class["description"])

    # Diastolic function
    if e_velocity and a_velocity:
        diastolic = assess_diastolic_function(
            e_velocity, a_velocity, e_prime, la_volume_index, tr_velocity_ms
        )
        result["parameters"]["diastolic_function"] = diastolic
        if "Grade II" in diastolic.get("grade", "") or "Grade III" in diastolic.get("grade", ""):
            result["warnings"].append(f"{diastolic['grade']}: {diastolic['description']}")
        result["findings"].append(f"Diastolic function: {diastolic.get('grade', 'N/A')} - {diastolic.get('grade_label', '')}")

    result["summary"] = "; ".join(result["findings"]) if result["findings"] else "No significant hemodynamic abnormalities"
    return result
