'''SQLite connection helpers.'''

from pathlib import Path
import sqlite3


def connect(path: Path) -> sqlite3.Connection:
    '''Open a SQLite connection for local metadata storage.'''
    return sqlite3.connect(path)

