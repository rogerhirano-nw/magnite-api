# magnite_client

A small Python client for the Magnite DV+ Performance Analytics REST API,
structured for the live-dashboard use case (scheduled pull → local cache →
fast dashboard read).

## Files

- `client.py` — the `MagniteClient` class. Handles auth, the create/poll/paginate
  loop, 429 backoff, and pagination via the "short page" heuristic.
- `refresh_cache.py` — scheduled-job entrypoint. Pulls each configured report
  into a SQLite table. Wire to cron / Airflow / systemd timer.
- `dashboard.py` — minimal Streamlit dashboard reading from the cache.

## Quickstart (once Magnite AM gives you the API key + secret)

```bash
pip install requests pandas streamlit

export MAGNITE_API_KEY=...
export MAGNITE_API_SECRET=...
export MAGNITE_ACCOUNT_ID=...  # your publisher ID

# 1. test auth and one report end-to-end
python -c "
from client import MagniteClient
c = MagniteClient(
    api_key='$MAGNITE_API_KEY',
    api_secret='$MAGNITE_API_SECRET',
    account_id='$MAGNITE_ACCOUNT_ID',
)
df = c.run_report(
    dimensions=['site', 'date'],
    metrics=['ad_requests', 'auctions', 'publisher_gross_revenue'],
    date_range='yesterday',
)
print(df.head())
print('rows:', len(df))
"

# 2. populate the cache
python refresh_cache.py

# 3. run the dashboard
streamlit run dashboard.py
```

## Switching from General to Prebid Analytics

The client is parametrized on dataset. The default is the General data set
(`"default"` in the URL path). Two changes needed for Prebid:

1. In `client.py`, confirm the Prebid path slug from the logged-in docs at
   <https://help.magnite.com/help/prebid-analytics-api> and update the
   `Dataset` literal type if it's not `"prebid"`.
2. In `refresh_cache.py`, pass `dataset="prebid"` in each report config and
   replace the dimension/metric lists with the Prebid-specific column keys
   from those docs.

Pattern is identical (POST create, GET status, GET paginated data), so the
client code itself doesn't need to change.

## Things that will bite you

- **Pull yesterday, not today.** Magnite's same-day data has latency.
- **500K row cap per report.** High-cardinality dims (zone_id, hour) blow
  through this fast. Break by date range or pre-filter.
- **5 reports in parallel max** — beyond that you get 429s. The client retries
  on 429 with backoff, but if you're running this hourly across many reports
  you'll want to serialize them rather than fire in parallel.
- **Datasets are siloed.** You can't mix General + First Party + Prebid dims
  in one call. One client call per dataset.
- **The 429 can lie.** The doc warns it sometimes means a system-wide issue,
  not actual queue pressure. If 429s persist for more than an hour on a single
  report, escalate to Magnite support.

## Production hardening to consider

- Move the cache from SQLite to Postgres / BigQuery if more than one person
  reads the dashboard concurrently.
- Idempotent upserts in `refresh_cache.py` keyed on (date + dimension cols)
  instead of `if_exists="append"` — otherwise re-running the same day double-counts.
- Secrets to a vault / env injection in your orchestrator rather than shell env.
- Structured logging (JSON) + alerting on `MagniteReportFailed` / `MagniteReportTimeout`.
- Cross-reference the bidder dimension against your `Newsweek_TAM_Bidder_Reference.xlsx`
  short codes to break down Prebid metrics by partner the way Confiant will eventually
  report it.
