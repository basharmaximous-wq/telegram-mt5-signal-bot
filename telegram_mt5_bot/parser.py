"""
Signal parser - extracts trade details from raw Telegram messages.

Supports formats like:
  BUY XAUUSD
  Entry: 1914 - 1911
  SL: 1909
  TP1: 1916
  TP2: 1918
  TP3: 1920

Also handles VIP-style gold calls:
  Gold sell now
  Gold sell now 4710 - 4713 SL: 4716 TP: 4708 TP: 4706 TP: 4704 TP: open
"""

import re
from dataclasses import dataclass, field
from typing import Optional


# Map common aliases to MT5 symbol names
SYMBOL_ALIASES = {
    "GOLD": "XAUUSD",
    "XAUUSD": "XAUUSD",
    "EU": "EURUSD",
    "GU": "GBPUSD",
    "GBPJPY": "GBPJPY",
    "UJ": "USDJPY",
    "UC": "USDCHF",
    "AU": "AUDUSD",
    "NU": "NZDUSD",
    "USDCAD": "USDCAD",
}


@dataclass
class Signal:
    symbol: str
    direction: str  # "BUY" or "SELL"
    entry_high: float  # top of entry range (or single entry)
    entry_low: float  # bottom of entry range
    sl: float
    tps: list = field(default_factory=list)  # [tp1, tp2, tp3, ...]
    raw: str = ""


def _find_number(text: str, *labels: str) -> Optional[float]:
    """Return the first float found after any of the given labels."""
    for label in labels:
        pattern = rf"(?i){re.escape(label)}\s*:?\s*([\d]+\.?[\d]*)"
        m = re.search(pattern, text)
        if m:
            return float(m.group(1))
    return None


def _find_range(text: str, *labels: str):
    """Return (high, low) from 'LABEL: 1914 - 1911' or 'LABEL: 1914'."""
    for label in labels:
        pattern = rf"(?i){re.escape(label)}\s*:?\s*([\d]+\.?[\d]*)\s*(?:[-\u2013]|to)?\s*([\d]+\.?[\d]*)?"
        m = re.search(pattern, text)
        if m:
            a = float(m.group(1))
            b = float(m.group(2)) if m.group(2) else a
            return (max(a, b), min(a, b))
    return None


def _find_unlabelled_range(text: str):
    """Return the first price range that is not attached to SL/TP labels."""
    pattern = r"(?<![A-Za-z])(\d+\.?\d*)\s*(?:[-\u2013]|to)\s*(\d+\.?\d*)"
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return None

    a = float(m.group(1))
    b = float(m.group(2))
    return (max(a, b), min(a, b))


def _find_all_numbers(text: str, *labels: str) -> list[float]:
    """Return every number found after repeated labels like TP: 4708 TP: 4706."""
    values = []
    for label in labels:
        pattern = rf"(?i){re.escape(label)}\s*:?\s*([\d]+\.?[\d]*)"
        for m in re.finditer(pattern, text):
            value = float(m.group(1))
            if value not in values:
                values.append(value)
    return values


def parse_signal_alert(text: str) -> Optional[dict]:
    """
    Return symbol/direction for an incomplete alert like 'Gold sell now'.
    These messages announce intent, then details often arrive shortly after.
    """
    text = text.strip()
    upper = text.upper()

    if not re.search(r"\b(BUY|SELL)\b", upper):
        return None

    if not re.search(r"\bNOW\b", upper):
        return None

    symbol = _extract_symbol(upper)
    if not symbol:
        return None

    direction = "BUY" if re.search(r"\bBUY\b", upper) else "SELL"
    return {"symbol": symbol, "direction": direction, "raw": text}


def parse_management_message(text: str) -> Optional[dict]:
    """Parse simple VIP trade-management instructions."""
    clean = text.strip()
    upper = clean.upper()

    if re.search(r"\bSETUP\s+FAILED|\bTRADE\s+FAILED", upper):
        return {"action": "SETUP_FAILED", "raw": clean}

    sl_match = re.search(r"\b(?:SL|STOP(?:\s+LOSS)?)\b[^\d]{0,30}(\d+\.?\d*)", clean, re.IGNORECASE)
    if sl_match:
        return {"action": "SET_SL", "price": float(sl_match.group(1)), "raw": clean}

    if re.search(r"\b(BE|BREAKEVEN|BREAK\s*EVEN)\b", upper):
        return {"action": "MOVE_BE", "raw": clean}

    if re.search(r"\bTAKE\s+SOME\s+PROFIT|\bTAKE\s+PROFITS|\bCLOSE\s+HALF|\bSECURE\s+PROFIT", upper):
        return {"action": "TAKE_PROFIT", "raw": clean}

    return None


def _extract_symbol(upper: str) -> Optional[str]:
    for alias, canonical in SYMBOL_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", upper):
            return canonical
    return None


def parse_signal(text: str) -> Optional[Signal]:
    """Return a Signal if the message looks like a trade signal, else None."""
    text = text.strip()
    upper = text.upper()

    # Must contain a direction word
    if not re.search(r"\b(BUY|SELL)\b", upper):
        return None

    # Extract direction
    direction = "BUY" if re.search(r"\bBUY\b", upper) else "SELL"

    # Extract symbol
    symbol = _extract_symbol(upper)
    if not symbol:
        return None

    # Entry range
    entry_range = (
        _find_range(text, "Entry", "Entries", "Entry zone")
        or _find_range(text, "Range", "Price")
        or _find_unlabelled_range(text)
    )
    if entry_range:
        entry_high, entry_low = entry_range
    else:
        # Maybe a single entry price after entry/@/at
        m = re.search(r"(?i)(?:entry|@|at)\s*:?\s*([\d]+\.?[\d]*)", text)
        if m:
            entry_high = entry_low = float(m.group(1))
        else:
            return None  # no entry found, so not a valid full signal

    # Stop loss
    sl = _find_number(text, "SL", "Stop Loss", "Stop", "S.L")
    if sl is None:
        return None  # SL is mandatory

    # Take profits - collect all TPn values
    tps = []
    for i in range(1, 6):
        tp = _find_number(text, f"TP{i}", f"TP {i}", f"T{i}", f"Target {i}", f"Take profit {i}")
        if tp:
            tps.append(tp)
    # Also collect repeated plain "TP:" values
    if not tps:
        tps = _find_all_numbers(text, "TP", "Take profit", "Target")

    if not tps:
        return None  # at least one TP is required

    return Signal(
        symbol=symbol,
        direction=direction,
        entry_high=entry_high,
        entry_low=entry_low,
        sl=sl,
        tps=tps,
        raw=text,
    )
