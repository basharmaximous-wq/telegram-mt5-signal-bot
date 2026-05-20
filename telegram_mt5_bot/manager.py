"""
Trade manager - monitors bot trades, moves SL to BE+, handles partial closes,
recovers open bot positions after restart, and applies simple VIP management
messages such as "breakeven", "take some profits", and "adjust SL to ...".
"""

import asyncio
import logging

import MetaTrader5 as mt5

from config import CONFIG
from logger import log_execution_event
from parser import Signal

log = logging.getLogger(__name__)


class TradeManager:
    def __init__(self):
        # ticket -> {signal, tp_index_reached, be_moved}
        self._tracked: dict[int, dict] = {}

    def register(self, trade: dict, signal):
        ticket = trade["ticket"]
        self._tracked[ticket] = {
            "signal": signal,
            "tp_index_reached": 0,
            "be_moved": False,
        }
        log.info(f"Manager tracking ticket {ticket}")

    def update_signal(self, ticket: int, signal):
        if ticket not in self._tracked:
            return
        self._tracked[ticket]["signal"] = signal
        self._tracked[ticket]["tp_index_reached"] = 0
        log.info(f"Manager updated ticket {ticket} with final SL/TP signal")

    def recover_open_positions(self):
        """Recover TGBot positions after a restart so BE/management continues."""
        if not self._connect():
            return
        try:
            positions = mt5.positions_get()
            if not positions:
                return
            recovered = 0
            for pos in positions:
                if "TGBot" not in str(getattr(pos, "comment", "")):
                    continue
                direction = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                signal = Signal(
                    symbol=pos.symbol,
                    direction=direction,
                    entry_high=pos.price_open,
                    entry_low=pos.price_open,
                    sl=pos.sl or 0.0,
                    tps=[pos.tp] if pos.tp else [],
                    raw="Recovered open MT5 position",
                )
                self._tracked[pos.ticket] = {
                    "signal": signal,
                    "tp_index_reached": 0,
                    "be_moved": bool(pos.sl and _sl_is_be_or_better(pos, pos.sl)),
                }
                recovered += 1
            if recovered:
                log.info(f"Recovered {recovered} open bot position(s) from MT5")
        finally:
            mt5.shutdown()

    async def monitor_loop(self):
        """Runs every N seconds and manages all tracked positions."""
        while True:
            await asyncio.sleep(CONFIG["monitor_interval_s"])
            try:
                self._check_positions()
            except Exception as e:
                log.error(f"Manager error: {e}")

    def handle_management_action(self, action: dict):
        name = action["action"]
        if name == "SET_SL":
            return self.move_all_sl(action["price"])
        if name == "MOVE_BE":
            return self.move_all_to_be()
        if name == "TAKE_PROFIT":
            fraction = CONFIG.get("manual_take_profit_close_fraction", 0.5)
            return self.close_all_fraction(fraction)
        if name == "SETUP_FAILED":
            if CONFIG.get("close_on_setup_failed", False):
                return self.close_all_fraction(1.0)
            log.warning("Setup failed message received. close_on_setup_failed is False, so positions were not closed.")
            return 0
        return 0

    def move_all_sl(self, sl: float) -> int:
        if not self._connect():
            return 0
        try:
            count = 0
            for pos in self._tracked_positions():
                if self._modify_sl_tp(pos, sl=sl, tp=pos.tp, action="manual_set_sl"):
                    count += 1
            log.info(f"Moved SL to {sl} on {count} tracked position(s)")
            return count
        finally:
            mt5.shutdown()

    def move_all_to_be(self) -> int:
        if not self._connect():
            return 0
        try:
            count = 0
            for pos in self._tracked_positions():
                if self._move_to_be(pos):
                    count += 1
                    if pos.ticket in self._tracked:
                        self._tracked[pos.ticket]["be_moved"] = True
            log.info(f"Moved {count} tracked position(s) to BE+")
            return count
        finally:
            mt5.shutdown()

    def close_all_fraction(self, fraction: float) -> int:
        if not self._connect():
            return 0
        try:
            count = 0
            for pos in self._tracked_positions():
                lot = round(pos.volume * fraction, 2)
                if fraction >= 1:
                    lot = pos.volume
                if lot >= 0.01 and self._partial_close(pos, lot, action="manual_partial_close"):
                    count += 1
            log.info(f"Closed {fraction:.0%} on {count} tracked position(s)")
            return count
        finally:
            mt5.shutdown()

    def close_trades(self, trades: list[dict]) -> int:
        tickets = {trade["ticket"] for trade in trades}
        if not self._connect():
            return 0
        try:
            count = 0
            positions = mt5.positions_get()
            if not positions:
                return 0
            for pos in positions:
                if pos.ticket in tickets and self._partial_close(pos, pos.volume, action="expired_vip_now_close"):
                    count += 1
            return count
        finally:
            mt5.shutdown()

    def _check_positions(self):
        if not self._connect():
            return
        try:
            positions = mt5.positions_get()
            if not positions:
                self._tracked.clear()
                return

            open_tickets = {p.ticket for p in positions}
            closed = [t for t in self._tracked if t not in open_tickets]
            for t in closed:
                log.info(f"Ticket {t} no longer open - removing from manager.")
                del self._tracked[t]

            for pos in positions:
                if pos.ticket not in self._tracked:
                    continue

                state = self._tracked[pos.ticket]
                signal = state["signal"]
                pip_size = _pip_size(pos.symbol)

                if pos.type == mt5.ORDER_TYPE_BUY:
                    profit_pips = (pos.price_current - pos.price_open) / pip_size
                else:
                    profit_pips = (pos.price_open - pos.price_current) / pip_size

                if (
                    not state["be_moved"]
                    and profit_pips >= CONFIG["be_trigger_pips"]
                    and not _sl_is_be_or_better(pos, pos.sl)
                ):
                    if self._move_to_be(pos):
                        state["be_moved"] = True

                tp_index = state["tp_index_reached"]
                tps = signal.tps
                if tp_index < len(tps) - 1:
                    next_tp = tps[tp_index]
                    if _price_past_tp(pos, next_tp):
                        fraction = CONFIG["tp1_partial_close"] if tp_index == 0 else CONFIG["tp2_partial_close"]
                        close_lot = round(pos.volume * fraction, 2)
                        if close_lot >= 0.01:
                            log.info(f"Ticket {pos.ticket}: TP{tp_index + 1} hit - partial close {close_lot} lot")
                            self._partial_close(pos, close_lot, action="tp_partial_close")
                        state["tp_index_reached"] += 1
        finally:
            mt5.shutdown()

    def _connect(self) -> bool:
        ok = mt5.initialize(
            login=CONFIG["mt5_login"],
            password=CONFIG["mt5_password"],
            server=CONFIG["mt5_server"],
        )
        if not ok:
            log.warning(f"MT5 init failed in manager: {mt5.last_error()}")
        return ok

    def _tracked_positions(self):
        positions = mt5.positions_get()
        if not positions:
            return []
        return [pos for pos in positions if pos.ticket in self._tracked]

    def _move_to_be(self, pos) -> bool:
        pip_size = _pip_size(pos.symbol)
        buffer = CONFIG.get("be_plus_pips", 0) * pip_size
        if pos.type == mt5.ORDER_TYPE_BUY:
            sl = round(pos.price_open + buffer, 5)
        else:
            sl = round(pos.price_open - buffer, 5)
        return self._modify_sl_tp(pos, sl=sl, tp=pos.tp, action="move_be")

    def _modify_sl_tp(self, pos, sl: float, tp: float, action: str) -> bool:
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": pos.symbol,
            "position": pos.ticket,
            "sl": sl,
            "tp": tp,
        }
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            log.info(f"Ticket {pos.ticket}: SL/TP updated sl={sl} tp={tp}")
            return True

        code = result.retcode if result else "no result"
        msg = f"SL/TP update failed for {pos.ticket}: {code}"
        log.warning(msg)
        log_execution_event("WARNING", action, symbol=pos.symbol, ticket=pos.ticket, retcode=code, last_error=str(mt5.last_error()), request=request, result=result, message=msg)
        return False

    def _partial_close(self, pos, lot, action: str) -> bool:
        close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick is None:
            log.warning(f"Cannot partial-close {pos.ticket}: no tick for {pos.symbol}")
            return False
        price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": lot,
            "type": close_type,
            "position": pos.ticket,
            "price": price,
            "comment": "TGBot partial",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            log.info(f"Partial close {lot} lot on ticket {pos.ticket}")
            return True

        code = result.retcode if result else "no result"
        msg = f"Partial close failed on {pos.ticket}: {code}"
        log.warning(msg)
        log_execution_event("WARNING", action, symbol=pos.symbol, ticket=pos.ticket, retcode=code, last_error=str(mt5.last_error()), request=request, result=result, message=msg)
        return False


def _pip_size(symbol: str) -> float:
    return 0.1 if "XAU" in symbol else 0.0001


def _be_price(pos) -> float:
    pip_size = _pip_size(pos.symbol)
    buffer = CONFIG.get("be_plus_pips", 0) * pip_size
    return pos.price_open + buffer if pos.type == mt5.ORDER_TYPE_BUY else pos.price_open - buffer


def _sl_is_be_or_better(pos, sl: float) -> bool:
    if not sl:
        return False
    be = _be_price(pos)
    if pos.type == mt5.ORDER_TYPE_BUY:
        return sl >= be
    return sl <= be


def _price_past_tp(pos, tp: float) -> bool:
    if pos.type == mt5.ORDER_TYPE_BUY:
        return pos.price_current >= tp
    return pos.price_current <= tp
