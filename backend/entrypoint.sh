#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os, time
from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]
engine = create_engine(url)
for i in range(60):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready")
        break
    except Exception as e:
        print(f"DB not ready ({i}): {e}")
        time.sleep(1)
else:
    raise SystemExit("Database not available")
PY

alembic upgrade head
python -m app.seed
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
