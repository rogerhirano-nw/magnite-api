# Claude Code notes for yield-dashboard

See `README.md` for project overview, files, and quickstart.

## Conventions
- Python (Streamlit dashboard + per-source clients). Cache layer is SQLite.
- One client module per data source (`*_client.py`), one `refresh_<ssp>` function in `refresh_cache.py`, called from `main()`.
- Pull yesterday's data, not today's — same-day data has latency.

## Things to never commit
- `.env`, `*.db`, `*.csv`, `.streamlit/secrets.toml` (already in `.gitignore`).
- Magnite / GAM / Pubmatic credentials.
