"""
SQLite logger — saves every signal and every trade to a local database.
"""

import sqlite3
import json
import logging
from datetime import datetime, timezone
from parser import Signal

DB_PATH = "bot_trades.db"
log = logging.getLogger(__name__)


def _conn():
    return sqlite3.connect(DB_PATH)


def _init_db():
    with _conn() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT,
                symbol    TEXT,
                direction TEXT,
                entry_high REAL,
                entry_low  REAL,
                sl        REAL,
                tps       TEXT,
                status    TEXT DEFAULT 'RECEIVED',
                reason    TEXT,
                raw_text  TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT,
                ticket    INTEGER,
                symbol    TEXT,
                direction TEXT,
                entry     REAL,
                sl        REAL,
                tps       TEXT,
                lot       REAL,
                entry_num INTEGER
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS execution_events (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT,
                level     TEXT,
                action    TEXT,
                symbol    TEXT,
                ticket    INTEGER,
                retcode   TEXT,
                last_error TEXT,
                request   TEXT,
                result    TEXT,
                message   TEXT
            )
        """)


_init_db()


def log_signal(signal: Signal, raw_text: str = "", status: str = "RECEIVED", reason: str = ""):
    try:
        with _conn() as db:
            db.execute(
                """INSERT INTO signals
                   (ts, symbol, direction, entry_high, entry_low, sl, tps, status, reason, raw_text)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    signal.symbol,
                    signal.direction,
                    signal.entry_high,
                    signal.entry_low,
                    signal.sl,
                    json.dumps(signal.tps),
                    status,
                    reason,
                    raw_text,
                )
            )
    except Exception as e:
        log.error(f"DB log_signal error: {e}")


def log_trade(trade: dict):
    try:
        with _conn() as db:
            db.execute(
                """INSERT INTO trades
                   (ts, ticket, symbol, direction, entry, sl, tps, lot, entry_num)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    trade["ticket"],
                    trade["symbol"],
                    trade["direction"],
                    trade["entry"],
                    trade["sl"],
                    json.dumps(trade["tps"]),
                    trade["lot"],
                    trade["entry_num"],
                )
            )
    except Exception as e:
        log.error(f"DB log_trade error: {e}")


def log_execution_event(
    level: str,
    action: str,
    symbol: str = "",
    ticket: int | None = None,
    retcode: str = "",
    last_error: str = "",
    request: dict | None = None,
    result: object = None,
    message: str = "",
):
    try:
        with _conn() as db:
            db.execute(
                """INSERT INTO execution_events
                   (ts, level, action, symbol, ticket, retcode, last_error, request, result, message)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    level,
                    action,
                    symbol,
                    ticket,
                    str(retcode or ""),
                    str(last_error or ""),
                    json.dumps(request or {}, default=str),
                    str(result or ""),
                    message,
                ),
            )
    except Exception as e:
        log.error(f"DB log_execution_event error: {e}")
