import sys
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

DB_DIR = Path(__file__).resolve().parent.parent / "backend" / "db"
sys.path.insert(0, str(DB_DIR))

from database import get_db


def test_get_db_yields_session():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    db.close()


def test_get_db_returns_session_type():
    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, Session)
    db.close()


def test_get_db_runs_query():
    db_gen = get_db()
    db = next(db_gen)
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1
    db.close()


def test_get_db_is_repeatable():
    db_gen1 = get_db()
    db1 = next(db_gen1)

    db_gen2 = get_db()
    db2 = next(db_gen2)

    assert db1 is not db2

    db1.close()
    db2.close()