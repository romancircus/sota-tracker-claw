"""Database utilities for SOTA Tracker."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Union, Generator


def get_db(db_path: Union[str, Path]) -> sqlite3.Connection:
    """
    Get a database connection with row factory.

    WARNING: Caller is responsible for closing the connection.
    Prefer using get_db_context() for auto-closing.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLite connection with Row factory enabled
    """
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    return db


@contextmanager
def get_db_context(db_path: Union[str, Path]) -> Generator[sqlite3.Connection, None, None]:
    """
    Get a database connection as a context manager that auto-closes.

    Usage:
        with get_db_context(path) as db:
            rows = db.execute(...).fetchall()
        # Connection automatically closed here

    Args:
        db_path: Path to SQLite database file

    Yields:
        SQLite connection with Row factory enabled
    """
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()
