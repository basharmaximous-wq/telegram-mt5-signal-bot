# Telegram -> MT5 Signal Bot

An automated trading assistant that listens to a Telegram VIP signal group,
parses gold/forex trade messages, validates them against risk rules, and sends
orders to MetaTrader 5.

This project was built for two-step Telegram signal flows such as:

```text
Gold buy now
```

followed by:

```text
Gold buy now 4700 - 4696
SL: 4691
TP: 4703
TP: 4705
TP: 4707
TP: open
```

## Features

- Telegram listener using Telethon
- MT5 execution through the official MetaTrader5 Python package
- XAUUSD / GOLD signal parsing
- Two-step VIP signal handling
- Immediate "buy now" / "sell now" first-layer entry
- Follow-up SL/TP modification
- Rule-based weighted layering
- Session, spread, max-position, SL, TP, and range validation
- Break-even plus buffer management
- Partial profit-taking at TP levels
- Manual management messages:
  - `breakeven`
  - `take some profits`
  - `adjust SL to 4688`
- Restart recovery for open bot trades
- SQLite logging for signals, trades, and execution errors
- MT5 health checker

## Trading Rules Engine

The bot does not blindly execute every message. Incoming signals pass through a
rule engine before orders are sent to MT5.

Implemented rules:

- **Session filter:** only trades during configured market hours, such as London
  and New York sessions.
- **Allowed symbols:** only approved instruments are tradable, with gold aliases
  normalized to `XAUUSD`.
- **Two-step signal flow:** can react to an initial `buy now` / `sell now`
  message, then apply full SL/TP details when the follow-up arrives.
- **Pending alert timeout:** if details do not arrive in time, the immediate
  entry can be closed instead of being left unmanaged.
- **SL validation:** stop loss must be on the correct side of the entry range.
- **TP validation:** take-profit levels must be on the correct side of the trade.
- **Entry range sanity:** rejects unusually wide ranges that may indicate a parse
  error or unsafe signal.
- **Spread check:** blocks trades when current spread is above the configured
  limit.
- **Max open trades:** prevents overexposure by limiting simultaneous open
  positions.
- **Range discipline:** avoids adding entries after price has moved beyond the
  configured grace range.
- **Weighted layering:** splits risk across entries, with larger lots deeper in
  the entry range.
- **Break-even plus:** once price moves in profit, SL can be moved past entry by
  a small configurable buffer.
- **Partial close management:** closes portions of the position at profit
  milestones.
- **Manual management parsing:** understands messages such as `breakeven`,
  `take some profits`, and `adjust SL to 4688`.
- **News blackout windows:** optional manually configured UTC windows can block
  new trades during high-volatility events.
- **Restart recovery:** reloads open bot-managed MT5 positions after restart.

## Risk Management

The bot is designed around controlled position sizing instead of fixed,
one-size-fits-all orders.

Risk controls:

- **Risk percentage:** each setup can be sized from a configured percentage of
  account balance, for example `1%` risk per signal.
- **Stop-loss distance:** the bot measures the distance between entry and SL in
  pips. A wider stop means smaller lot size; a tighter stop allows a larger lot
  within the configured limits.
- **Pip model:** for gold, the bot treats `0.1` price movement as one pip. For
  most forex pairs, it uses `0.0001`.
- **Lot cap:** `max_lot_per_signal` limits total exposure even if the calculated
  risk size would be larger.
- **Layered entries:** total risk is split across multiple entries instead of
  placing one large order immediately.
- **Weighted lots:** deeper entries can receive larger lots, so the bot starts
  smaller and scales only if price moves further into the planned range.
- **Max open positions:** prevents the account from taking too many active
  setups at once.
- **Break-even plus:** when price moves enough in profit, SL can move beyond
  entry to reduce downside.
- **Partial profit taking:** the bot can close part of the position at TP levels,
  securing a percentage of the win while leaving some exposure for continuation.

Example:

```text
Balance: $5,000
Risk: 1%
Max risk: $50
Entry: 4700
SL: 4695
Gold pip size: 0.1
Distance to SL: 50 pips
```

The bot uses that pip distance, symbol tick value, and account balance to
estimate a lot size, then caps it with `max_lot_per_signal` and splits it across
the configured number of entries.

## Requirements

- Windows PC
- Python 3.10+
- MetaTrader 5 installed and logged in
- Telegram account that belongs to the signal group

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Configuration

Copy the example config:

```powershell
copy config.example.py config.py
```

Then fill in `config.py` with your private Telegram and MT5 details.

Never commit `config.py`, `.session` files, `bot.log`, or `bot_trades.db`.
They are ignored by `.gitignore`.

## Run

First verify MT5 can see XAUUSD:

```powershell
python check_mt5.py
```

Then start the bot:

```powershell
python bot.py
```

## Safety Notes

This project can place real trades if connected to a live MT5 account. Test on
a demo account first. Trading involves risk, and automation should be monitored
carefully.
