"""
Run this script ONCE to fix the `incident_type` column issue in `incident_history`.

The DB table has a column `incident_type` (NOT NULL, no default) that conflicts
with the SQLAlchemy model which uses `inc_type`. This script renames `incident_type`
to `inc_type` if needed, or adds `inc_type` if missing.

Usage:
    python migrate2.py
"""

from sqlalchemy import create_engine, text, inspect

MYSQL_USER = "sp_user"
MYSQL_PASSWORD = ""        # ← put your actual password here
MYSQL_HOST = "localhost"
MYSQL_DB = "sp_core"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_columns(conn, table: str):
    inspector = inspect(conn)
    return [c["name"] for c in inspector.get_columns(table)]


def run():
    with engine.begin() as conn:
        cols = get_columns(conn, "incident_history")
        print(f"Current columns in incident_history: {cols}")

        has_incident_type = "incident_type" in cols
        has_inc_type = "inc_type" in cols

        if has_inc_type and not has_incident_type:
            print("✅  Column 'inc_type' already exists and 'incident_type' is absent. Nothing to do.")

        elif has_incident_type and not has_inc_type:
            # Rename incident_type → inc_type
            conn.execute(text(
                "ALTER TABLE incident_history CHANGE COLUMN incident_type inc_type VARCHAR(50) NOT NULL"
            ))
            print("✅  Renamed 'incident_type' → 'inc_type' in 'incident_history'.")

        elif has_incident_type and has_inc_type:
            # Both exist — drop the stale incident_type column
            conn.execute(text(
                "ALTER TABLE incident_history DROP COLUMN incident_type"
            ))
            print("✅  Dropped duplicate 'incident_type' column (kept 'inc_type').")

        else:
            # Neither exists — add inc_type
            conn.execute(text(
                "ALTER TABLE incident_history ADD COLUMN inc_type VARCHAR(50) NOT NULL DEFAULT ''"
            ))
            print("✅  Added missing 'inc_type' column to 'incident_history'.")

        # Also ensure image_url exists (from previous migration)
        cols = get_columns(conn, "incident_history")
        if "image_url" not in cols:
            conn.execute(text(
                "ALTER TABLE incident_history ADD COLUMN image_url VARCHAR(500) NULL"
            ))
            print("✅  Also added missing 'image_url' column.")
        else:
            print("✅  'image_url' column already present.")

        print("\nDone! Final columns:", get_columns(conn, "incident_history"))


if __name__ == "__main__":
    run()