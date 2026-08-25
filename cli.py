#!/usr/bin/env python3
"""
CLI for Echocardiography Hemodynamic Calculator.

Provides commands for cardiac output, stroke volume, EF classification,
mitral valve area, PASP, and diastolic function assessment.
"""
import argparse
import json
import sys

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


def cmd_co(args):
    """Calculate cardiac output and index."""
    sv = calculate_stroke_volume_from_diameter(args.lvot_diameter, args.lvot_vti)
    co = calculate_cardiac_output(sv, args.hr)

    print("=" * 60)
    print("  CARDIAC OUTPUT CALCULATION")
    print("=" * 60)
    lvot_area = calculate_lvot_area(args.lvot_diameter)
    print(f"  LVOT diameter:     {args.lvot_diameter} cm")
    print(f"  LVOT area:         {lvot_area:.2f} cm^2")
    print(f"  LVOT VTI:          {args.lvot_vti} cm")
    print(f"  Stroke Volume:     {sv:.1f} mL")
    print(f"  Heart Rate:        {args.hr} bpm")
    print(f"  Cardiac Output:    {co:.2f} L/min")

    if args.height and args.weight:
        bsa = calculate_bsa(args.height, args.weight)
        ci = calculate_cardiac_index(co, bsa)
        print(f"  BSA:               {bsa:.2f} m^2")
        print(f"  Cardiac Index:     {ci:.2f} L/min/m^2")
        if ci < 2.2:
            print("  ** LOW cardiac index - possible low output state")
        elif ci > 4.0:
            print("  ** HIGH cardiac index - consider high output state")

    if args.json:
        result = {"sv_ml": round(sv, 1), "co_lpm": round(co, 2)}
        if args.height and args.weight:
            result["bsa"] = round(bsa, 2)
            result["ci"] = round(ci, 2)
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_ef(args):
    """Classify ejection fraction."""
    result = classify_ejection_fraction(args.ef)

    print("=" * 60)
    print("  EJECTION FRACTION CLASSIFICATION")
    print("=" * 60)
    print(f"  EF:                {result['ef_percent']}%")
    print(f"  Category:          {result['label']}")
    print(f"  Description:       {result['description']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_mva(args):
    """Calculate mitral valve area from PHT."""
    mva = calculate_mva_pressure_half_time(args.pht)
    result = classify_mva(mva)

    print("=" * 60)
    print("  MITRAL VALVE AREA (PHT Method)")
    print("=" * 60)
    print(f"  Pressure Half-Time: {args.pht} ms")
    print(f"  MVA:               {result['mva_cm2']} cm^2")
    print(f"  Severity:          {result['description']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_pasp(args):
    """Calculate pulmonary artery systolic pressure."""
    pasp = calculate_pasp(args.tr_velocity, args.rap)
    result = classify_pasp(pasp)

    print("=" * 60)
    print("  PULMONARY ARTERY SYSTOLIC PRESSURE")
    print("=" * 60)
    print(f"  TR velocity:       {args.tr_velocity} m/s")
    print(f"  RAP:               {args.rap} mmHg")
    print(f"  PASP:              {result['pasp_mmhg']} mmHg")
    print(f"  Classification:    {result['description']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_diastolic(args):
    """Assess diastolic function."""
    result = assess_diastolic_function(
        e_velocity=args.e_velocity,
        a_velocity=args.a_velocity,
        e_prime=args.e_prime,
        la_volume_index=args.la_volume_index,
        tr_velocity=args.tr_velocity,
    )

    print("=" * 60)
    print("  DIASTOLIC FUNCTION ASSESSMENT")
    print("=" * 60)
    print(f"  E velocity:        {result['e_velocity']} cm/s")
    print(f"  A velocity:        {result['a_velocity']} cm/s")
    print(f"  E/A ratio:         {result['e_a_ratio']}")
    if "e_prime" in result:
        print(f"  e' velocity:       {result['e_prime']} cm/s")
        print(f"  E/e' ratio:        {result['e_e_prime']}")
    if "la_volume_index" in result:
        print(f"  LA volume index:   {result['la_volume_index']} mL/m^2")
        print(f"  LA enlarged:       {'Yes' if result['la_enlarged'] else 'No'}")
    print(f"  Grade:             {result['grade']}")
    print(f"  Label:             {result['grade_label']}")
    print(f"  LA pressure:       {result['la_pressure_estimate']}")
    print(f"  Description:       {result['description']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_assess(args):
    """Run comprehensive hemodynamic assessment."""
    result = comprehensive_hemodynamic_assessment(
        lvot_diameter_cm=args.lvot_diameter,
        lvot_vti_cm=args.lvot_vti,
        heart_rate_bpm=args.hr,
        height_cm=args.height,
        weight_kg=args.weight,
        ef_percent=args.ef,
        pht_ms=args.pht,
        tr_velocity_ms=args.tr_velocity,
        rap_mmhg=args.rap,
        e_velocity=args.e_velocity,
        a_velocity=args.a_velocity,
        e_prime=args.e_prime,
        la_volume_index=args.la_volume_index,
    )

    print("=" * 60)
    print("  COMPREHENSIVE HEMODYNAMIC ASSESSMENT")
    print("=" * 60)

    params = result["parameters"]
    if "stroke_volume_ml" in params:
        print(f"  Stroke Volume:     {params['stroke_volume_ml']} mL")
    if "cardiac_output_lpm" in params:
        print(f"  Cardiac Output:    {params['cardiac_output_lpm']} L/min")
    if "cardiac_index" in params:
        print(f"  Cardiac Index:     {params['cardiac_index']} L/min/m^2")
    if "ejection_fraction" in params:
        ef = params["ejection_fraction"]
        print(f"  EF:                {ef['ef_percent']}% ({ef['label']})")
    if "mitral_valve_area" in params:
        mva = params["mitral_valve_area"]
        print(f"  MVA:               {mva['mva_cm2']} cm^2 ({mva['severity']})")
    if "pasp" in params:
        p = params["pasp"]
        print(f"  PASP:              {p['pasp_mmhg']} mmHg ({p['classification']})")
    if "diastolic_function" in params:
        d = params["diastolic_function"]
        print(f"  Diastolic:         {d['grade']} - {d['grade_label']}")

    if result["findings"]:
        print("\n  FINDINGS:")
        for f in result["findings"]:
            print(f"    - {f}")

    if result["warnings"]:
        print("\n  WARNINGS:")
        for w in result["warnings"]:
            print(f"    !! {w}")

    print(f"\n  SUMMARY: {result['summary']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="echo-hemodynamics",
        description="Echocardiography Hemodynamic Calculator",
    )
    parser.add_argument("--json", action="store_true", help="Also output JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Cardiac output
    p_co = subparsers.add_parser("co", help="Calculate cardiac output/index")
    p_co.add_argument("--lvot-diameter", type=float, required=True, help="LVOT diameter in cm")
    p_co.add_argument("--lvot-vti", type=float, required=True, help="LVOT VTI in cm")
    p_co.add_argument("--hr", type=float, required=True, help="Heart rate in bpm")
    p_co.add_argument("--height", type=float, help="Height in cm (for CI)")
    p_co.add_argument("--weight", type=float, help="Weight in kg (for CI)")

    # EF classification
    p_ef = subparsers.add_parser("ef", help="Classify ejection fraction")
    p_ef.add_argument("--ef", type=float, required=True, help="Ejection fraction in %%")

    # MVA
    p_mva = subparsers.add_parser("mva", help="Mitral valve area (PHT method)")
    p_mva.add_argument("--pht", type=float, required=True, help="Pressure half-time in ms")

    # PASP
    p_pasp = subparsers.add_parser("pasp", help="Pulmonary artery systolic pressure")
    p_pasp.add_argument("--tr-velocity", type=float, required=True, help="TR velocity in m/s")
    p_pasp.add_argument("--rap", type=float, default=10.0, help="RAP in mmHg (default 10)")

    # Diastolic
    p_diast = subparsers.add_parser("diastolic", help="Diastolic function assessment")
    p_diast.add_argument("--e-velocity", type=float, required=True, help="E velocity cm/s")
    p_diast.add_argument("--a-velocity", type=float, required=True, help="A velocity cm/s")
    p_diast.add_argument("--e-prime", type=float, help="e' velocity cm/s")
    p_diast.add_argument("--la-volume-index", type=float, help="LA volume index mL/m^2")
    p_diast.add_argument("--tr-velocity", type=float, help="TR velocity m/s")

    # Comprehensive
    p_all = subparsers.add_parser("assess", help="Comprehensive hemodynamic assessment")
    p_all.add_argument("--lvot-diameter", type=float, help="LVOT diameter cm")
    p_all.add_argument("--lvot-vti", type=float, help="LVOT VTI cm")
    p_all.add_argument("--hr", type=float, help="Heart rate bpm")
    p_all.add_argument("--height", type=float, help="Height cm")
    p_all.add_argument("--weight", type=float, help="Weight kg")
    p_all.add_argument("--ef", type=float, help="EF %%")
    p_all.add_argument("--pht", type=float, help="PHT ms")
    p_all.add_argument("--tr-velocity", type=float, help="TR velocity m/s")
    p_all.add_argument("--rap", type=float, default=10.0, help="RAP mmHg")
    p_all.add_argument("--e-velocity", type=float, help="E velocity cm/s")
    p_all.add_argument("--a-velocity", type=float, help="A velocity cm/s")
    p_all.add_argument("--e-prime", type=float, help="e' velocity cm/s")
    p_all.add_argument("--la-volume-index", type=float, help="LA volume index mL/m^2")

    args = parser.parse_args(argv)

    commands = {
        "co": cmd_co,
        "ef": cmd_ef,
        "mva": cmd_mva,
        "pasp": cmd_pasp,
        "diastolic": cmd_diastolic,
        "assess": cmd_assess,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
