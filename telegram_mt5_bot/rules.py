"""
Rules engine — validates a parsed signal against your trading rules
before any order is sent to MT5.
"""

from datetime import datetime, timezone
from config import CONFIG
from parser import Signal
import MetaTrader5 as mt5


def validate_signal(signal: Signal) -> tuple[bool, str]:
    """
    Run all rule checks. Returns (True, "") if signal passes,
    or (False, reason_string) if it should be rejected.
    """

    checks = [
        _check_pair_allowed,
        _check_session,
        _check_sl_validity,
        _check_tp_validity,
        _check_entry_range_sanity,
        _check_news_blackout,
        _check_spread,
        _check_max_open_signals,
    ]

    for check in checks:
        ok, reason = check(signal)
        if not ok:
            return False, reason

    return True, ""


def validate_alert(alert: dict) -> tuple[bool, str]:
    """
    Validate an immediate VIP alert like 'Gold sell now' before opening
    the first market layer. SL/TP checks are intentionally skipped because
    those values arrive in the follow-up details message.
    """

    checks = [
        _check_alert_pair_allowed,
        _check_session,
        _check_news_blackout,
        _check_alert_spread,
        _check_max_open_signals,
    ]

    for check in checks:
        ok, reason = check(alert)
        if not ok:
            return False, reason

    return True, ""


# ─────────────────────────────────────────────────────────────────────────────

def _check_pair_allowed(signal: Signal):
    if signal.symbol not in CONFIG["allowed_pairs"]:
        return False, f"Pair {signal.symbol} not in allowed list"
    return True, ""


def _check_alert_pair_allowed(alert: dict):
    symbol = alert["symbol"]
    if symbol not in CONFIG["allowed_pairs"]:
        return False, f"Pair {symbol} not in allowed list"
    return True, ""


def _check_session(signal: Signal):
    now_utc_hour = datetime.now(timezone.utc).hour
    start = CONFIG["session_start_utc"]
    end   = CONFIG["session_end_utc"]
    if not (start <= now_utc_hour < end):
        return False, f"Outside session window ({start}–{end} UTC). Current hour: {now_utc_hour}"
    return True, ""


def _check_sl_validity(signal: Signal):
    """SL must be on the correct side of the entry range."""
    if signal.direction == "BUY":
        if signal.sl >= signal.entry_low:
            return False, f"BUY signal: SL {signal.sl} must be below entry low {signal.entry_low}"
    else:
        if signal.sl <= signal.entry_high:
            return False, f"SELL signal: SL {signal.sl} must be above entry high {signal.entry_high}"
    return True, ""


def _check_tp_validity(signal: Signal):
    """All TPs must be on the correct side of the entry range."""
    for i, tp in enumerate(signal.tps, 1):
        if signal.direction == "BUY":
            if tp <= signal.entry_high:
                return False, f"BUY signal: TP{i} {tp} must be above entry high {signal.entry_high}"
        else:
            if tp >= signal.entry_low:
                return False, f"SELL signal: TP{i} {tp} must be below entry low {signal.entry_low}"
    return True, ""


def _check_entry_range_sanity(signal: Signal):
    """Entry range must not be absurdly wide (e.g. > 200 pips) — likely a parse error."""
    pip_size = 0.01 if "JPY" in signal.symbol else 0.0001
    if "XAU" in signal.symbol or "GOLD" in signal.symbol:
        pip_size = 0.1
    range_pips = abs(signal.entry_high - signal.entry_low) / pip_size
    if range_pips > 200:
        return False, f"Entry range too wide: {range_pips:.0f} pips — possible parse error"
    return True, ""


def _check_news_blackout(signal):
    now = datetime.now(timezone.utc)
    for window in CONFIG.get("news_blackout_windows_utc", []):
        try:
            start = datetime.strptime(window["start"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            end = datetime.strptime(window["end"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue
        if start <= now <= end:
            reason = window.get("reason", "news blackout")
            return False, f"Blocked during {reason} ({window['start']} - {window['end']} UTC)"
    return True, ""


def _check_spread(signal: Signal):
    """Reject if current spread is excessive (> 30 pips for gold, > 5 pips for fx)."""
    return _check_symbol_spread(signal.symbol)


def _check_alert_spread(alert: dict):
    return _check_symbol_spread(alert["symbol"])


def _check_symbol_spread(symbol: str):
    """Reject if current spread is excessive (> 30 pips for gold, > 5 pips for fx)."""
    if not mt5.initialize():
        return True, ""  # if MT5 unavailable, skip spread check

    try:
        sym_info = mt5.symbol_info(symbol)
        if sym_info is None:
            return False, f"Symbol {symbol} not found in MT5"

        if not sym_info.visible and not mt5.symbol_select(symbol, True):
            return False, f"Could not select symbol {symbol} in MT5"

        info = mt5.symbol_info_tick(symbol)
        if info is None:
            return False, f"Cannot get live tick for {symbol}"

        pip_size = 0.1 if "XAU" in symbol else 0.0001
        spread_pips = abs(info.ask - info.bid) / pip_size
        max_spread  = 30 if "XAU" in symbol else 5

        if spread_pips > max_spread:
            return False, f"Spread too wide: {spread_pips:.1f} pips (max {max_spread})"
        return True, ""
    finally:
        mt5.shutdown()


def _check_max_open_signals(signal: Signal):
    """Don't exceed max open positions."""
    if not mt5.initialize():
        return True, ""

    try:
        positions = mt5.positions_get()
        if positions is None:
            return True, ""

        if len(positions) >= CONFIG["max_open_signals"]:
            return False, f"Already {len(positions)} open positions (max {CONFIG['max_open_signals']})"
        return True, ""
    finally:
        mt5.shutdown()
