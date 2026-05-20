<!-- 
  Ultra-Violet Trading Bot README
  Dark Mode Optimized | 3D Glowing Effects | Animated SVG Headers
  Note: GitHub's markdown strips style/script blocks. The animations are delivered via
  an embedded SVG that includes its own CSS and HTML, a clever workaround.
-->

<p align="center">
  <!-- Animated Neon Banner SVG with Gradient Glow -->
  <svg width="800" height="150" viewBox="0 0 800 150" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#D8B4FE" />
        <stop offset="50%" stop-color="#A855F7" />
        <stop offset="100%" stop-color="#7E22CE" />
      </linearGradient>
      <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="5" />
        <feMerge>
          <feMergeNode in="offsetblur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
      <filter id="glowSubtle" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="15" />
        <feMerge>
          <feMergeNode in="offsetblur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
      <style>
        @keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
        .neonText { font-family: monospace; fill: url(#neonGradient); font-weight: bold; filter: url(#glow); }
        .glowCircle { fill: #7E22CE; filter: url(#glowSubtle); animation: pulse 2s infinite; }
        .floatingBox { animation: float 3s ease-in-out infinite; }
      </style>
    </defs>
    <!-- Background dark layer -->
    <rect width="100%" height="100%" fill="#0B0014" />
    <!-- Subtle grid pattern -->
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#2D1B3D" stroke-width="0.5" />
    </pattern>
    <rect width="100%" height="100%" fill="url(#grid)" />
    
    <!-- Animated decorative floating element -->
    <g class="floatingBox">
      <polygon points="400,30 420,50 400,70 380,50" fill="#A855F7" opacity="0.4" />
    </g>
    
    <!-- Main Title -->
    <text x="400" y="80" text-anchor="middle" font-size="48" class="neonText" letter-spacing="4">
      TELEGRAM ➜ MT5 EXECUTION
    </text>
    <text x="400" y="115" text-anchor="middle" font-size="18" fill="#9CA3AF" font-family="monospace" letter-spacing="2">
      WEIGHTED LAYERING • RISK-FIRST PROTOCOL • 3D GLOW VISUALS
    </text>
  </svg>
</p>

---

## ⚡ Hot & Sexy Features: The Neo-Trading Suite

| Module | Description |
|--------|-------------|
| **Telegram Listener** | Uses `Telethon` – reads only designated VIP groups. |
| **MT5 Execution** | Official MetaTrader5 package – live or demo. |
| **Gold / Forex Parser** | Recognizes `XAUUSD`, `GOLD`, `XAU`, and major pairs. |
| **Two‑Step Signal Memory** | Matches follow‑up SL/TP to a pending immediate entry. |
| **Rule‑Based Layering** | Splits total risk across entries; deeper = larger lot. |
| **Session Filter** | Only trades during London & New York (configurable). |
| **Spread Sentinel** | Blocks trades if spread exceeds limit. |
| **Max Open Positions** | Prevents over‑commitment. |
| **Entry Range Sanity** | Rejects improbably wide ranges (likely parsing errors). |
| **SL & TP Validation** | Ensures stop and targets are on the correct side of price. |
| **Pending Alert Timeout** | Closes unprotected entry if follow‑up never arrives. |
| **Break‑Even + Buffer** | Moves SL beyond entry once profit buffer is hit. |
| **Partial Profit Taking** | Closes configurable percentage at each TP level. |
| **Manual Management Commands** | `breakeven`, `take some profits`, `adjust SL to 4688`. |
| **News Blackout Windows** | UTC‑based windows – no new trades during volatility. |
| **Restart Recovery** | Reloads open bot‑managed positions after restart. |
| **SQLite Ledger** | Logs signals, trades, errors – immutable audit trail. |
| **MT5 Health Checker** | Verifies connection and symbol availability. |

---

## 🧠 Wealth Preservation Framework (Risk Engine)

This bot emulates a **private trading desk**:

### 1. Risk‑First Sizing
- A **risk percentage** (e.g. 1% of current balance) is set per signal.
- The bot measures **pip distance** from entry to SL.
- Lot size = (Risk Amount) / (Pip Distance × Pip Value)

> **Example**  
> Balance: $5,000 | Risk: 1% → $50 at stake  
> Gold: entry 4700, SL 4695 → distance = 50 pips (0.1 per pip)  
> Lot size is calculated, then capped by `max_lot_per_signal`.

### 2. Weighted Layering
Instead of one large market order, risk is split across multiple price levels.  
Deeper entries receive **larger lots** – the bot starts small and scales only if price moves deeper into the planned range.

### 3. Pip Model
- Gold / XAUUSD → `0.1` = 1 pip  
- Forex (EURUSD, GBPUSD etc.) → `0.0001` = 1 pip  

### 4. Conservative Overrides
- **Max open positions** – hard limit on concurrent setups  
- **Spread check** – avoids paying excessive slippage  
- **Entry range grace** – if price has moved too far, the signal is rejected  

### 5. Break‑Even Plus
Once price moves **X pips** in profit, the stop loss is moved **beyond entry** by a small buffer (e.g. +2 pips).  
The trade becomes *risk‑free* while still allowing upside.

### 6. Partial Profit Taking
At each TP level, a **percentage** of the position is closed (e.g. 30% at TP1, 30% at TP2, 40% left for “open”).  
This secures realized gains while keeping a runner.

---

## 🏦 Requirements – The Private Client Setup

- **Windows PC** (dedicated or VPS recommended)
- **Python 3.10+**
- **MetaTrader 5** installed, logged in, and authorized for automated trading
- **Telegram account** that is a member of the target VIP signal group

### Install Dependencies

```powershell
pip install -r requirements.txt
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
