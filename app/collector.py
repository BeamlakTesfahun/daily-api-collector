import os
import json
import time
import logging
from datetime import datetime, timezone

import requests
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

DATABASE_URL = os.getenv("DATABASE_URL")
API_URL = os.getenv("API_URL", "https://api.coindesk.com/v1/bpi/currentprice.json")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS api_snapshots (
  id SERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL,
  payload JSONB NOT NULL
);
"""

INSERT_SQL = """
INSERT INTO api_snapshots (source, fetched_at, payload)
VALUES (%s, %s, %s::jsonb);
"""

def fetch_json(url: str, retries: int = 3, backoff: float = 1.5) -> dict:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            logging.warning(f"Fetch failed (attempt {attempt}/{retries}): {e}")
            time.sleep(backoff ** attempt)
    raise RuntimeError(f"Failed to fetch JSON after {retries} retries: {last_err}")

def main():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    logging.info(f"Fetching from API: {API_URL}")
    payload = fetch_json(API_URL)

    fetched_at = datetime.now(timezone.utc)
    source = API_URL

    logging.info("Connecting to Postgres...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            cur.execute(INSERT_SQL, (source, fetched_at, json.dumps(payload)))
    finally:
        conn.close()

    logging.info("Saved snapshot to Postgres")
    logging.info(f"fetched_at={fetched_at.isoformat()}")

if __name__ == "__main__":
    main()
