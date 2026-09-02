# Echo Hemodynamic Agent

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines & Standards:** `AHA/ACC Practice Guidelines & ESC Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Echo Hemodynamic Agent** is an advanced analytical and computational platform implementing Valvular Continuity Equation & Diastolic Dysfunction Grader.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_lvot_area()`**: Calculate LVOT (Left Ventricular Outflow Tract) cross-sectional area.

Area = pi x (diameter/2)^2

Args:
    lvot_diameter_cm: LVOT diameter in centimeters (typically 2.0-2.5 cm)

Returns:
    LVOT area in cm^2
- **`calculate_stroke_volume()`**: Calculate Stroke Volume from LVOT measurements.

SV = LVOT area x LVOT VTI

The VTI (Velocity Time Integral) is obtained by tracing the spectral
Doppler envelope of flow through the LVOT.

Args:
    lvot_area_cm2: LVOT cross-sectional area in cm^2
    lvot_vti_cm: LVOT VTI in cm (from pulsed-wave Doppler)

Returns:
    Stroke volume in mL (cm^3)
- **`calculate_stroke_volume_from_diameter()`**: Calculate Stroke Volume directly from LVOT diameter and VTI.

SV = pi x (d/2)^2 x VTI

Args:
    lvot_diameter_cm: LVOT diameter in cm
    lvot_vti_cm: LVOT VTI in cm

Returns:
    Stroke volume in mL
- **`calculate_cardiac_output()`**: Calculate Cardiac Output.

CO = SV x HR

Args:
    stroke_volume_ml: Stroke volume in mL
    heart_rate_bpm: Heart rate in beats per minute

Returns:
    Cardiac output in L/min
- **`calculate_bsa()`**: Calculate Body Surface Area.

Du Bois formula: BSA = 0.007184 x height^0.725 x weight^0.425
Mosteller formula: BSA = sqrt((height x weight) / 3600)

Args:
    height_cm: Height in centimeters
    weight_kg: Weight in kilograms
    formula: "du_bois" (default) or "mosteller"

Returns:
    BSA in m^2

---

## 📐 Mathematical Formulation & Logic

```text
  Calculate LVOT (Left Ventricular Outflow Tract) cross-sectional area.
  Calculate Stroke Volume from LVOT measurements.
  Calculate Stroke Volume directly from LVOT diameter and VTI.
  area = calculate_lvot_area(lvot_diameter_cm)
  return calculate_stroke_volume(area, lvot_vti_cm)
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --json <value> --lvot-diameter <value> --lvot-vti <value> --hr <value>
```

### Parameter Reference
- `--json`: Specifies input measurement or parameter value.
- `--lvot-diameter`: Specifies input measurement or parameter value.
- `--lvot-vti`: Specifies input measurement or parameter value.
- `--hr`: Specifies input measurement or parameter value.
- `--height`: Specifies input measurement or parameter value.
- `--weight`: Specifies input measurement or parameter value.
- `--ef`: Specifies input measurement or parameter value.
- `--pht`: Specifies input measurement or parameter value.
- `--tr-velocity`: Specifies input measurement or parameter value.
- `--rap`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Parameter / observation metric | Required |
| `patient_synthetic_id` | Parameter / observation metric | Required |
| `metric_primary` | Parameter / observation metric | Required |
| `metric_secondary` | Parameter / observation metric | Required |
| `is_stat` | Parameter / observation metric | Required |
| `status_flag` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t echo-hemodynamic-agent .
docker run -p 8000:8000 echo-hemodynamic-agent
```
