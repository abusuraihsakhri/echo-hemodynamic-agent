# Echo Hemodynamic Agent

### [Open the Live Application →](https://abusuraihsakhri.github.io/echo-hemodynamic-agent/)

Echocardiography hemodynamic calculator with a dependency-free browser interface, Python CLI, and an optional FastAPI audit service.

**Use for education, research, and synthetic test data only.** Results are arithmetic estimates rather than clinical diagnoses or treatment recommendations. Do not submit patient identifiers or protected health information.

## Capabilities

- **Browser calculator:** LVOT area, stroke volume, cardiac output, Du Bois BSA, cardiac index, pressure-half-time estimated mitral valve area, estimated RV systolic pressure, LVEF, E/A and E/e-prime ratios.
- **Python calculator:** Equivalent core measurements, basic EF-range classification and a **legacy simplified** diastolic-pattern heuristic.
- **API / agent audit:** Separate generic numerical threshold demonstration, synthetic case processing, HMAC-chained audit events and health/metrics endpoints. Its generic thresholds are **not** validated echo severity criteria.
- **Tests:** Python pytest suite, Node-based browser arithmetic tests and GitHub Actions CI.

The browser calculator uses native JavaScript and no backend, Pyodide, analytics or third-party scripts. Pressing **Calculate** processes measurements locally; **Download results** produces a local JSON file. The separate optional API form transmits data only when submitted to a running same-origin FastAPI server. The simple identifier-pattern guard is **not** a substitute for complete PHI de-identification.

## Browser use

Open `web/index.html` in a modern browser and enter the required LVOT diameter, LVOT VTI, and heart rate. Optional measurement groups require their corresponding paired fields. The standalone calculator works without network access.

The live GitHub Pages calculator is deployed directly from `web/` and verified after deployment by automated HTTP checks of both the page and its JavaScript.

## Python calculator

Python 3.10–3.12 is tested in CI. Install from the repository root:

```bash
python -m pip install -e ".[api,test]"
python cli.py co --lvot-diameter 2.0 --lvot-vti 22 --hr 72 --json
python cli.py ef --ef 45
python cli.py mva --pht 220
python cli.py pasp --tr-velocity 3 --rap 10
python cli.py diastolic --e-velocity 80 --a-velocity 60 --e-prime 10
python cli.py assess --ef 45 --pht 150
```

The installed `echo-hemodynamics` console script provides the same calculator commands. The existing `echo-hemodynamic-engine` and `echo_hemodynamic_agent_app.py` entry points remain available for the separate generic agent audit workflow.

**Clinical interpretation limitations:** The E/A and E/e-prime ratios alone do not establish diastolic function grade or heart failure with preserved ejection fraction. The Python grading method is a legacy heuristic, **not** an implementation of the [2025 ASE diastolic function guideline](https://www.asecho.org/guideline/left-ventricular-diastolic-function-by-echo/), which superseded the 2016 approach. Pressure-half-time mitral valve area and Doppler RV systolic pressure estimates have important acquisition and clinical limitations; estimated RVSP does not independently diagnose pulmonary hypertension.

## Optional local API

```bash
python -m pip install -e ".[api]"
uvicorn agents.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the calculator and optional same-origin audit form. API endpoints are `GET /health`, `POST /api/audit`, `POST /api/chat`, `GET /api/audit/logs`, and `GET /metrics`. The API is designed for local synthetic examples and is **not** an authenticated, HIPAA-compliant service. Do not expose it to untrusted networks.

For Docker Compose, generate a unique audit key and set `AUDIT_SECRET_KEY` in your environment or an ignored `.env` file before running `docker compose up --build`. The default Compose port binding is localhost-only. Without a configured audit key, direct Python execution creates an ephemeral key: historic chain signatures will not survive restarts.

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

For automated tests:

```bash
pytest -q
node --test tests/test_browser_calculator.cjs
```

## Technology and license

Python (standard-library calculations), Pydantic 2, optional FastAPI/Uvicorn, plain HTML/CSS/JavaScript, Node test runner, and GitHub Actions. The static calculator is intended for current desktop and mobile browsers supporting ES2020 and the standard DOM APIs.

Licensed under [MIT](LICENSE).
