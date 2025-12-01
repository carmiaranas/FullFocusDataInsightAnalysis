# Braking Telemetry Overlay — MVP

This small Streamlit app overlays braking telemetry from two CSV files (Trainer = Driver 1 vs Trainee = Driver 2).

Folder layout (project root):

- `Trainer/` — CSV files for Driver 1 (trainer)
- `Trainee/` — CSV files for Driver 2 (trainee)
- `app.py` — Streamlit app
- `requirements.txt` — Python deps

Quick start (Windows PowerShell):

```markdown
# Braking Telemetry Overlay — MVP

This small Streamlit app overlays braking telemetry from two CSV files (Trainer = Driver 1 vs Trainee = Driver 2).

Folder layout (project root):

- `Trainer/` — CSV files for Driver 1 (trainer)
- `Trainee/` — CSV files for Driver 2 (trainee)
- `app.py` — Streamlit app
- `requirements.txt` — Python deps

Install & run (Windows PowerShell)

1. Create a virtual environment and install dependencies (recommended):

```powershell
cd 'C:\Users\carmi.marie.aranas\FullFocusBrakePressureAnalysis'
# Create venv
python -m venv .venv
# Activate (PowerShell)
. .\.venv\Scripts\Activate.ps1
# Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
# Run the app
streamlit run app.py
```

2. If PowerShell blocks `Activate.ps1` due to execution policy, run Streamlit directly with the venv Python instead of activating:

```powershell
cd 'C:\Users\carmi.marie.aranas\FullFocusBrakePressureAnalysis'
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Quick smoke test (verify required packages are importable):

```powershell
.venv\Scripts\python.exe -c "import streamlit,pandas,altair; print('smoke-test: OK')"
```

Usage notes:
- The app will auto-detect columns named like `Distance` or `Time`, and a `Brake`/`Brake_Pressure` column.
- Use the sidebar to pick Trainer/Trainee files and adjust column mapping or smoothing.
- The main chart shows both traces overlaid (Trainer in yellow, Trainee in cyan). Drag/zoom on the chart to change the visible range; axes update interactively.

If you want additional features (live-updating summary when you zoom, shaded brake zones, lap-sync), tell me which option you prefer and I will implement it.

``` 
