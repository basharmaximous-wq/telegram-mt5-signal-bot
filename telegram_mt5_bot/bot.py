"""
Telegram -> MT5 Signal Bot
Listens to your VIP Telegram group and auto-executes trades in MetaTrader 5.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone

from telethon import TelegramClient, events

from config import CONFIG
from parser import Signal, parse_management_message, parse_signal, parse_signal_alert
from rules import validate_alert, validate_signal
from executor import apply_signal_to_trades, execute_alert_market, execute_signal, get_last_execution_error, health_check
from manager import TradeManager
from logger import log_signal, log_trade

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

PENDING_ALERT_TTL_S = CONFIG.get("pending_alert_timeout_s", 180)


def _pending_is_fresh(pending_alert: dict | None) -> bool:
    if not pending_alert:
        return False
    age_s = (datetime.now(timezone.utc) - pending_alert["ts"]).total_seconds()
    return age_s <= PENDING_ALERT_TTL_S


def _combine_with_pending(text: str, pending_alert: dict | None) -> str:
    """Add the earlier "buy/sell now" context if details arrive separately."""
    if not _pending_is_fresh(pending_alert):
        return text

    upper = text.upper()
    has_direction = "BUY" in upper or "SELL" in upper
    has_symbol = pending_alert["symbol"] in upper or "GOLD" in upper
    if has_direction and has_symbol:
        return text

    return f"{pending_alert['raw']}\n{text}"


def _pending_matches_signal(pending_alert: dict | None, signal: Signal) -> bool:
    return (
        _pending_is_fresh(pending_alert)
        and pending_alert["symbol"] == signal.symbol
        and pending_alert["direction"] == signal.direction
    )


async def _resolve_vip_group(client: TelegramClient):
    """
    Resolve CONFIG['vip_group'] as an ID/username first, then as an exact
    Telegram dialog title if the group is private.
    """
    target = CONFIG["vip_group"]

    try:
        return await client.get_input_entity(target)
    except (TypeError, ValueError):
        pass

    target_text = str(target).strip()
    async for dialog in client.iter_dialogs():
        if dialog.name == target_text:
            return dialog.entity

    raise ValueError(
        f"Cannot find Telegram group '{target_text}'. "
        "Use the exact group title, public username, or numeric chat ID in config.py."
    )


async def main():
    log.info("Starting Telegram -> MT5 bot...")

    client = TelegramClient(
        "session_user",
        CONFIG["api_id"],
        CONFIG["api_hash"],
    )

    manager = TradeManager()
    pending_alert = None

    await client.start(phone=CONFIG["phone"])
    vip_group = await _resolve_vip_group(client)
    log.info(f"Listening to group: {CONFIG['vip_group']}")

    ok, health_reason = health_check("XAUUSD")
    if ok:
        log.info(health_reason)
    else:
        log.warning(f"MT5 health check failed: {health_reason}")

    manager.recover_open_positions()

    async def pending_alert_watch_loop():
        nonlocal pending_alert
        while True:
            await asyncio.sleep(5)
            if pending_alert and not _pending_is_fresh(pending_alert):
                trades = pending_alert.get("trades", [])
                closed = manager.close_trades(trades)
                log.warning(
                    f"VIP details did not arrive within {PENDING_ALERT_TTL_S}s. "
                    f"Closed {closed} immediate trade(s)."
                )
                pending_alert = None

    @client.on(events.NewMessage(chats=vip_group))
    async def on_message(event):
        nonlocal pending_alert

        text = event.message.message
        if not text:
            return

        log.info(f"New message received:\n{text}")

        signal = parse_signal(text)
        matching_pending_alert = None

        if not signal and _pending_is_fresh(pending_alert):
            combined_text = _combine_with_pending(text, pending_alert)
            signal = parse_signal(combined_text)
            if signal:
                text = combined_text

        if not signal:
            management_action = parse_management_message(text)
            if management_action:
                changed = manager.handle_management_action(management_action)
                log.info(f"Applied management action {management_action['action']} to {changed} position(s).")
                return

            alert = parse_signal_alert(text)
            if alert:
                ok, reason = validate_alert(alert)
                if not ok:
                    log.warning(f"VIP now alert rejected: {reason}")
                    return

                trades = execute_alert_market(alert)
                if not trades:
                    log.error("VIP now alert execution failed. No trade placed.")
                    return

                placeholder = Signal(
                    symbol=alert["symbol"],
                    direction=alert["direction"],
                    entry_high=trades[0]["entry"],
                    entry_low=trades[0]["entry"],
                    sl=0.0,
                    tps=[],
                    raw=text,
                )
                for t in trades:
                    log_trade(t)
                    manager.register(t, placeholder)

                pending_alert = {
                    **alert,
                    "ts": datetime.now(timezone.utc),
                    "trades": trades,
                }
                log.info(f"Opened and stored pending VIP alert: {alert['symbol']} {alert['direction']}")
                return

            log.info("Message is not a trade signal. Skipping.")
            return

        if _pending_matches_signal(pending_alert, signal):
            matching_pending_alert = pending_alert
        else:
            pending_alert = None

        log.info(f"Parsed signal: {signal}")
        log_signal(signal, raw_text=text)

        ok, reason = validate_signal(signal)
        if not ok:
            log.warning(f"Signal rejected: {reason}")
            log_signal(signal, raw_text=text, status="REJECTED", reason=reason)
            return

        log.info("Signal passed all rules. Executing...")

        existing_trades = matching_pending_alert.get("trades", []) if matching_pending_alert else []
        updated_trades = apply_signal_to_trades(signal, existing_trades)
        for t in updated_trades:
            manager.update_signal(t["ticket"], signal)

        if existing_trades and not updated_trades:
            log.error("Could not attach SL/TP to the immediate VIP entry. Not placing more layers.")
            log_signal(signal, raw_text=text, status="EXEC_FAILED", reason="VIP now SL/TP update failed")
            return

        trades = execute_signal(signal, skip_entries=len(existing_trades))
        pending_alert = None

        if not trades:
            if not updated_trades:
                reason = get_last_execution_error()
                log.error(f"Execution failed. No trades placed or updated. {reason}")
                log_signal(signal, raw_text=text, status="EXEC_FAILED", reason=reason)
                return
            log.info("No new layered orders placed; updated the immediate VIP entry only.")

        log.info(f"Placed {len(trades)} new order(s), updated {len(updated_trades)} existing order(s).")
        for t in trades:
            log_trade(t)

        for t in trades:
            manager.register(t, signal)

    asyncio.create_task(manager.monitor_loop())
    asyncio.create_task(pending_alert_watch_loop())

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
