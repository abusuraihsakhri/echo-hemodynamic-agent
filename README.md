# Echocardiography Hemodynamic Calculator

> **Cardiology - Echocardiography**  
> Reference Standards: ASE/EACVI Guidelines

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)

---

## Overview

A real, functional echocardiography hemodynamic calculator implementing:

- **Cardiac Output**: CO = SV x HR, where SV = LVOT area x LVOT VTI
- **Stroke Volume**: From LVOT diameter and pulsed-wave Doppler VTI
- **Cardiac Index**: CI = CO / BSA (Du Bois or Mosteller formula)
- **Ejection Fraction**: Classification per ACC/AHA (Normal, HFpEF, HFmrEF, HFrEF)
- **Mitral Valve Area**: PHT method (MVA = 220 / PHT)
- **Pulmonary Artery Systolic Pressure**: PASP = 4 x (TR velocity)^2 + RAP
- **Diastolic Function**: E/A ratio, E/e' ratio with ASE/EACVI 2016 grading

**No external dependencies** - uses only Python standard library.

---

## Quick Start

```bash
# Calculate cardiac output
python cli.py co --lvot-diameter 2.0 --lvot-vti 22 --hr 72

# Calculate cardiac output with index
python cli.py co --lvot-diameter 2.0 --lvot-vti 22 --hr 72 --height 170 --weight 70

# Classify ejection fraction
python cli.py ef --ef 35

# Mitral valve area from PHT
python cli.py mva --pht 220

# Pulmonary artery systolic pressure
python cli.py pasp --tr-velocity 3.0 --rap 10

# Diastolic function assessment
python cli.py diastolic --e-velocity 80 --a-velocity 60 --e-prime 10

# Comprehensive assessment
python cli.py assess --lvot-diameter 2.0 --lvot-vti 22 --hr 72 --ef 45 --pht 150 --tr-velocity 2.8 --e-velocity 90 --a-velocity 50 --e-prime 8
```

---

## Python API

```python
from echo_hemodynamics import (
    calculate_stroke_volume_from_diameter,
    calculate_cardiac_output,
    calculate_bsa,
    calculate_cardiac_index,
    classify_ejection_fraction,
    calculate_mva_pressure_half_time,
    calculate_pasp,
    assess_diastolic_function,
)

# Cardiac output
sv = calculate_stroke_volume_from_diameter(lvot_diameter_cm=2.0, lvot_vti_cm=22.0)
co = calculate_cardiac_output(sv, heart_rate_bpm=72)
# -> CO ~3.8 L/min (depends on LVOT area)

# EF classification
result = classify_ejection_fraction(35)
# -> {'category': 'hfref', 'label': 'HFrEF', ...}

# MVA from PHT
mva = calculate_mva_pressure_half_time(pht_ms=220)
# -> 1.0 cm^2 (severe MS)

# PASP
pasp = calculate_pasp(tr_velocity_ms=3.0, rap_mmhg=10)
# -> 46.0 mmHg

# Diastolic grading
result = assess_diastolic_function(e_velocity=80, a_velocity=60, e_prime=10)
# -> {'grade': 'Normal', 'e_a_ratio': 1.33, 'e_e_prime': 8.0, ...}
```

---

## Clinical Reference

### Ejection Fraction Categories
| Category | EF Range | Description |
|----------|----------|-------------|
| Normal | >=55% | Normal LV systolic function |
| HFpEF | >=50% | HF with preserved EF |
| HFmrEF | 40-49% | HF with mildly reduced EF |
| HFrEF | <40% | HF with reduced EF |

### Diastolic Function Grading (ASE/EACVI 2016)
| Grade | E/A | E/e' | LA Pressure |
|-------|-----|------|-------------|
| Normal | 0.8-2.0 | <8 | Normal |
| Grade I | <0.8 | <8 | Normal |
| Grade II | 0.8-2.0 | 9-12 | Elevated |
| Grade III | >2.0 | >13 | Markedly elevated |

### Normal Hemodynamic Values
| Parameter | Normal Range |
|-----------|-------------|
| Stroke Volume | 60-100 mL |
| Cardiac Output | 4.0-8.0 L/min |
| Cardiac Index | 2.5-4.0 L/min/m^2 |
| MVA | 4.0-6.0 cm^2 |
| PASP | 15-30 mmHg |

---

## Disclaimer

This tool is for **educational and clinical decision support purposes only**. It does not replace professional medical judgment. Always correlate with clinical context.

## License

MIT License. See [LICENSE](LICENSE) for details.
