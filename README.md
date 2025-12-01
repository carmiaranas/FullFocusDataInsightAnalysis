# Braking Telemetry Overlay — MVP

This small Streamlit app overlays braking telemetry from two CSV files (Trainer = Driver 1 vs Trainee = Driver 2).

Folder layout (project root):

- `Trainer/` — CSV files for Driver 1 (trainer)
- `Trainee/` — CSV files for Driver 2 (trainee)
- `app.py` — Streamlit app
- `requirements.txt` — Python deps

Quick start (Windows PowerShell):

```powershell
python -m venv .venv; ; .\.venv\Scripts\Activate.ps1; 
pip install -r requirements.txt
streamlit run app.py
```

Usage notes:
- The app will auto-detect columns named like `Distance` or `Time`, and a `Brake`/`Brake_Pressure` column.
- Use the sidebar to pick Trainer/Trainee files and adjust column mapping or smoothing.
- The main chart shows both traces overlaid (Trainer in yellow, Trainee in cyan).

If you want enhancements (brake zones shading, sync by lap fraction, export PNG), tell me and I will add them.
