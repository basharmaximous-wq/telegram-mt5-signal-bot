"""
MT5 executor - places immediate and layered orders, and records detailed
execution errors so failures can be diagnosed from the database.
"""

import logging

import MetaTrader5 as mt5

from config import CONFIG
from logger import log_execution_event
from parser import Signal

log = logging.getLogger(__name__)
LAST_EXECUTION_ERROR = ""


def _set_error(message: str, action: str = "", symbol: str = "", request: dict | None = None, result=None):
    global LAST_EXECUTION_ERROR
    LAST_EXECUTION_ERROR = message
    log.error(message)
    log_execution_event(
        "ERROR",
        action,
        symbol=symbol,
        retcode=getattr(result, "retcode", ""),
        last_error=str(mt5.last_error()),
        request=request,
        result=result,
        message=message,
    )


def get_last_execution_error() -> str:
    return LAST_EXECUTION_ERROR


def _connect() -> bool:
    if mt5.initialize(
        login=CONFIG["mt5_login"],
        password=CONFIG["mt5_password"],
        server=CONFIG["mt5_server"],
    ):
        return True
    _set_error(f"MT5 init failed: {mt5.last_error()}", action="connect")
    return False


def _ensure_symbol(symbol: str) -> bool:
    """Make sure the broker symbol is available to MT5 Python calls."""
    info = mt5.symbol_info(symbol)
    if info is None:
        _set_error(
            f"MT5 symbol not found: {symbol}. Check the exact broker symbol name in Market Watch.",
            action="ensure_symbol",
            symbol=symbol,
        )
        return False

    if not info.visible and not mt5.symbol_select(symbol, True):
        _set_error(
            f"MT5 could not select symbol: {symbol}. Last error: {mt5.last_error()}",
            action="ensure_symbol",
            symbol=symbol,
        )
        return False

    return True


def health_check(symbol: str = "XAUUSD") -> tuple[bool, str]:
    """Verify MT5 is connected, trading is allowed, and a live tick exists."""
    if not _connect():
        return False, get_last_execution_error()
    try:
        account = mt5.account_info()
        if account is None:
            return False, f"MT5 account is not available: {mt5.last_error()}"
        if not _ensure_symbol(symbol):
            return False, get_last_execution_error()
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False, f"No live tick for {symbol}: {mt5.last_error()}"
        if not getattr(account, "trade_allowed", True):
            return False, "MT5 account trading is not allowed"
        return True, f"MT5 OK: {symbol} bid={tick.bid} ask={tick.ask}"
    finally:
        mt5.shutdown()


def _total_lot(symbol: str, sl_pips: float) -> float:
    """
    Calculate total lot based on risk% of balance.
    Falls back to max_lot_per_signal if calculation fails.
    """
    account = mt5.account_info()
    if account is None:
        base_lot = CONFIG["max_lot_per_signal"]
    else:
        balance = account.balance
        risk_amount = balance * (CONFIG["risk_per_trade_pct"] / 100)
        sym_info = mt5.symbol_info(symbol)
        if sym_info and sl_pips > 0 and sym_info.trade_tick_size:
            pip_value = sym_info.trade_tick_value / sym_info.trade_tick_size * (
                0.1 if "XAU" in symbol else 0.0001
            )
            base_lot = risk_amount / (sl_pips * pip_value) if pip_value > 0 else CONFIG["max_lot_per_signal"]
        else:
            base_lot = CONFIG["max_lot_per_signal"]

    return min(base_lot, CONFIG["max_lot_per_signal"])


def _layer_lots(symbol: str, sl_pips: float, count: int) -> list[float]:
    total_lot = _total_lot(symbol, sl_pips)
    if count <= 1:
        return [round(max(total_lot, 0.01), 2)]

    if CONFIG.get("weighted_layering", True):
        weights = list(range(1, count + 1))
        weight_sum = sum(weights)
        lots = [round(max(total_lot * weight / weight_sum, 0.01), 2) for weight in weights]
    else:
        lots = [round(max(total_lot / count, 0.01), 2) for _ in range(count)]

    diff = round(total_lot - sum(lots), 2)
    lots[-1] = round(max(lots[-1] + diff, 0.01), 2)
    return lots


def _sl_pips(signal: Signal) -> float:
    pip_size = 0.1 if "XAU" in signal.symbol else 0.0001
    ref_entry = signal.entry_low if signal.direction == "BUY" else signal.entry_high
    return abs(ref_entry - signal.sl) / pip_size


def _fallback_lot_per_entry() -> float:
    return _layer_lots("XAUUSD", 0, CONFIG["num_entries"])[0]


def execute_alert_market(alert: dict) -> list[dict]:
    """
    Open the first VIP 'now' layer immediately without SL/TP.
    The follow-up details message should modify this position with SL/TP.
    """
    if not _connect():
        return []

    symbol = alert["symbol"]
    direction = alert["direction"]
    if not _ensure_symbol(symbol):
        mt5.shutdown()
        return []

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        _set_error(
            f"Cannot get tick for {symbol}. Make sure MT5 is logged in and receiving live prices.",
            action="vip_now_tick",
            symbol=symbol,
        )
        mt5.shutdown()
        return []

    order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
    exec_price = tick.ask if direction == "BUY" else tick.bid
    lot = _fallback_lot_per_entry()

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": exec_price,
        "sl": 0.0,
        "tp": 0.0,
        "comment": "TGBot VIP now",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    mt5.shutdown()

    if not result or result.retcode != mt5.TRADE_RETCODE_DONE:
        code = result.retcode if result else "no result"
        _set_error(f"VIP now entry failed: retcode={code}", action="vip_now_order", symbol=symbol, request=request, result=result)
        return []

    trade_info = {
        "ticket": result.order,
        "symbol": symbol,
        "direction": direction,
        "entry": exec_price,
        "sl": 0.0,
        "tps": [],
        "lot": lot,
        "entry_num": 1,
    }
    log.info(f"VIP now entry: {direction} {symbol} {lot} lot @ {exec_price}")
    return [trade_info]


def apply_signal_to_trades(signal: Signal, trades: list[dict]) -> list[dict]:
    """Attach the final SL/TP values to already-open VIP now trades."""
    if not trades:
        return []

    if not _connect():
        return []

    updated = []
    for trade in trades:
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": trade["symbol"],
            "position": trade["ticket"],
            "sl": signal.sl,
            "tp": signal.tps[0] if signal.tps else 0.0,
        }
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            trade.update({"sl": signal.sl, "tps": signal.tps})
            updated.append(trade)
            log.info(f"Updated VIP now ticket {trade['ticket']} with SL/TP")
        else:
            code = result.retcode if result else "no result"
            msg = f"Could not update VIP now ticket {trade['ticket']}: {code}"
            log.warning(msg)
            log_execution_event(
                "WARNING",
                "update_sltp",
                symbol=trade["symbol"],
                ticket=trade["ticket"],
                retcode=code,
                last_error=str(mt5.last_error()),
                request=request,
                result=result,
                message=msg,
            )

    mt5.shutdown()
    return updated


def execute_signal(signal: Signal, skip_entries: int = 0) -> list[dict]:
    """Place layered limit orders. Returns list of trade result dicts."""
    if not _connect():
        return []

    results = []
    n = CONFIG["num_entries"]
    pip_size = 0.1 if "XAU" in signal.symbol else 0.0001
    if not _ensure_symbol(signal.symbol):
        mt5.shutdown()
        return []

    lots = _layer_lots(signal.symbol, _sl_pips(signal), n)

    if signal.entry_high == signal.entry_low:
        entry_prices = [signal.entry_high] * n
    else:
        step = (signal.entry_high - signal.entry_low) / max(n - 1, 1)
        entry_prices = [round(signal.entry_high - i * step, 5) for i in range(n)]

    tick = mt5.symbol_info_tick(signal.symbol)
    if tick is None:
        _set_error(
            f"Cannot get tick for {signal.symbol}. Make sure MT5 is logged in and receiving live prices.",
            action="signal_tick",
            symbol=signal.symbol,
        )
        mt5.shutdown()
        return []

    current_price = tick.ask if signal.direction == "BUY" else tick.bid

    for i, price in enumerate(entry_prices):
        if i < skip_entries:
            continue

        lot = lots[i]
        distance_pips = abs(current_price - price) / pip_size
        past_buy_range = signal.direction == "BUY" and current_price < signal.entry_low
        past_sell_range = signal.direction == "SELL" and current_price > signal.entry_high
        if distance_pips > CONFIG["grace_pips"] and (past_buy_range or past_sell_range):
            log.warning(f"Entry {i + 1} at {price} is {distance_pips:.1f} pips beyond grace limit. Skipping.")
            continue

        if distance_pips <= 3:
            order_type = mt5.ORDER_TYPE_BUY if signal.direction == "BUY" else mt5.ORDER_TYPE_SELL
            exec_price = current_price
            action = mt5.TRADE_ACTION_DEAL
        else:
            order_type = mt5.ORDER_TYPE_BUY_LIMIT if signal.direction == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT
            exec_price = price
            action = mt5.TRADE_ACTION_PENDING

        request = {
            "action": action,
            "symbol": signal.symbol,
            "volume": lot,
            "type": order_type,
            "price": exec_price,
            "sl": signal.sl,
            "tp": signal.tps[0] if signal.tps else 0.0,
            "comment": f"TGBot E{i + 1}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        placed_retcode = getattr(mt5, "TRADE_RETCODE_PLACED", mt5.TRADE_RETCODE_DONE)
        ok_retcode = result and result.retcode in (mt5.TRADE_RETCODE_DONE, placed_retcode)
        if ok_retcode:
            trade_info = {
                "ticket": result.order,
                "symbol": signal.symbol,
                "direction": signal.direction,
                "entry": exec_price,
                "sl": signal.sl,
                "tps": signal.tps,
                "lot": lot,
                "entry_num": i + 1,
            }
            results.append(trade_info)
            log.info(f"Entry {i + 1}: {order_type} {signal.symbol} {lot} lot @ {exec_price}")
        else:
            code = result.retcode if result else "no result"
            _set_error(f"Entry {i + 1} failed: retcode={code}", action="signal_order", symbol=signal.symbol, request=request, result=result)

    mt5.shutdown()
    return results
