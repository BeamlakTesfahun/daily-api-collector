A tiny script that fetches JSON from a public API and stores raw snapshots into Postgres (JSONB). Designed as a “daily script” style project (scraping/data collection/automation).

## Features

-   Fetches JSON from an API endpoint
-   Stores full payload in Postgres as JSONB
-   Runs via Docker Compose (db + script container)
-   Basic retry/backoff + logs for troubleshooting

## Tech

-   Python (requests, psycopg2)
-   Postgres (JSONB)
-   Docker + Docker Compose

## Run

```bash
docker compose up --build
```
