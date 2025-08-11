
# MUFC · 5 temaer (Streamlit demo)

Klar til Streamlit Cloud og iPhone.

## Filer
- `mufc_mock_app.py` — app
- `requirements.txt` — pakker

## Deploy på iPhone
1) Opret public GitHub-repo (fx `mufc-demo`).
2) Upload `mufc_mock_app.py` + `requirements.txt`.
3) Streamlit Cloud → **New app** → repo = dit, branch = `main`, main file = `mufc_mock_app.py` → **Deploy**.

## Valgfrit (live data)
- Tilføj secret: `FOOTBALL_DATA_API_KEY` i Streamlit → Settings → Secrets.

## Fejl du kan møde
- `ModuleNotFoundError`: mangler `requirements.txt`.
- `File not found`: forkert `Main file path` (skal være `mufc_mock_app.py` i repo-roden).
- Tom side: tryk **Rerun** eller drej telefonen vandret.
