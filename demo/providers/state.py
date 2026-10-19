"""SQLite transactions keep provider state independent of client releases."""
from contextlib import contextmanager
import ipaddress
import json
from pathlib import Path
import sqlite3

from fastapi import HTTPException, Request


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                INSERT OR IGNORE INTO settings VALUES ('version','1');
                CREATE TABLE IF NOT EXISTS payments (id TEXT PRIMARY KEY, key TEXT UNIQUE, payload TEXT, result TEXT);
                CREATE TABLE IF NOT EXISTS holds (id TEXT PRIMARY KEY, key TEXT UNIQUE, payload TEXT,
                    show_id TEXT, seats TEXT, amount INTEGER, expires_at REAL, payment_id TEXT, result TEXT);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @property
    def version(self):
        with self.connect() as db:
            return int(db.execute("SELECT value FROM settings WHERE key='version'").fetchone()[0])

    def switch(self, version):
        if type(version) is not int or version not in (1, 2):
            raise HTTPException(422, 'Choose provider version 1 or 2')
        with self.connect() as db:
            db.execute("UPDATE settings SET value=? WHERE key='version'", (str(version),))
        return {'version': version}


def local_admin(request: Request):
    host = request.client.host if request.client else ''
    try:
        allowed = ipaddress.ip_address(host).is_loopback
    except ValueError:
        allowed = host == 'testclient'
    if not allowed:
        raise HTTPException(403, 'Provider controls are available only on this computer')
    origin = request.headers.get('origin')
    if origin:
        from urllib.parse import urlsplit
        parsed = urlsplit(origin)
        if parsed.scheme not in {'http', 'https'} or parsed.netloc != request.headers.get('host'):
            raise HTTPException(403, 'Cross-origin provider controls are blocked')


def required_text(body, key):
    value = body.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > 160:
        raise HTTPException(422, f'{key} must be a nonempty string of at most 160 characters')
    return value


def fingerprint(body):
    return json.dumps(body, sort_keys=True, separators=(',', ':'))
