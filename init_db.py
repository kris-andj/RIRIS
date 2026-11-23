from pathlib import Path

import seed
from backend.settings import engine

SCHEMA = Path(__file__).resolve().parent / "schema.sql"


def main():
    with engine.begin() as conn:
        conn.exec_driver_sql(SCHEMA.read_text(encoding="utf-8"))
    seed.main()


if __name__ == "__main__":
    main()
