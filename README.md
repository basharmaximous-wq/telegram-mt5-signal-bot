<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=500&color=A855F7&background=0B0014&center=true&vCenter=true&width=700&height=80&lines=TELEGRAM+%E2%9E%9C+MT5;WEIGHTED+LAYERING;RISK-FIRST+PROTOCOL;⚖️+RISK+ENGINE+ACTIVE" alt="Typing SVG" />
</p>

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/Python-3.10%2B-8A2BE2?style=for-the-badge&logo=python&logoColor=white&labelColor=0B0014" /></a>
  <a href="https://www.metatrader5.com/"><img src="https://img.shields.io/badge/MT5-7E22CE?style=for-the-badge&logo=metatrader5&logoColor=white&labelColor=0B0014" /></a>
  <a href="https://my.telegram.org/"><img src="https://img.shields.io/badge/Telegram-API-D8B4FE?style=for-the-badge&logo=telegram&logoColor=white&labelColor=0B0014" /></a>
</p>

<p align="center">
  <i>“Fortune favors the disciplined. Risk is not taken — it is allocated.”</i>
</p>

---

<!-- WHITE LASER ANIMATED DIVIDER -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&height=2&width=800&text=&fontColor=fff&animation=twinkling" />
</p>

## 🏛️ EXECUTIVE SUMMARY – THE SIGNAL VAULT

A **bespoke execution engine** bridging a private [Telegram](https://telegram.org/) VIP group with [MetaTrader 5](https://www.metatrader5.com/).  
Designed for **two‑step signal flows** — immediate entry followed by full SL/TP structure.  
Operates like a **family office trading desk**:

- 🤫 Listens silently
- 🛡️ Validates against a conservative rule framework
- ⚖️ Splits exposure across **weighted, layered entries**
- 💰 Manages partial profits, break‑even buffers, and manual override commands

> *No blind execution. No greed. No uncontrolled exposure.*

---

## ⚡ FEATURE SUITE – NEO‑TRADING ENGINE

| Module | Description |
|--------|-------------|
| **Telegram Listener** | [`Telethon`](https://docs.telethon.dev/) – reads only designated VIP groups |
| **MT5 Execution** | Official [`MetaTrader5`](https://www.metatrader5.com/en/terminal/help/algotrading/ctrade) Python package |
| **Gold / Forex Parser** | Recognises `XAUUSD`, `GOLD`, `XAU`, and major pairs |
| **Two‑Step Signal Memory** | Matches follow‑up SL/TP to a pending immediate entry |
| **Rule‑Based Layering** | Splits total risk across entries; deeper = larger lot |
| **Session Filter** | Only trades during London & New York (configurable) |
| **Spread Sentinel** | Blocks trades if spread exceeds limit |
| **Max Open Positions** | Prevents over‑commitment |
| **Entry Range Sanity** | Rejects improbably wide ranges |
| **SL & TP Validation** | Ensures stop and targets are on the correct side |
| **Pending Alert Timeout** | Closes unprotected entry if follow‑up never arrives |
| **Break‑Even + Buffer** | Moves SL beyond entry once profit buffer is hit |
| **Partial Profit Taking** | Closes configurable % at each TP level |
| **Manual Management** | `breakeven`, `take some profits`, `adjust SL to 4688` |
| **News Blackout Windows** | UTC‑based – no new trades during volatility |
| **Restart Recovery** | Reloads open bot‑managed positions after restart |
| **SQLite Ledger** | Immutable audit trail for signals, trades, errors |
| **MT5 Health Checker** | Verifies connection and symbol availability |

---

## 🧠 WEALTH PRESERVATION FRAMEWORK – RISK ENGINE

This bot does **not** use fixed lots. It emulates a **private trading desk**:

### 1. Risk‑First Sizing
- Risk percentage of current balance (e.g. 1%)
- Pip distance measured from entry to SL
- **Lot size = (Risk Amount) / (Pip Distance × Pip Value)**

> **Example**  
> Balance: $5,000 | Risk: 1% → $50 at stake  
> Gold: entry 4700, SL 4695 → distance = 50 pips (0.1 per pip)  
> Lot size calculated, then capped by `max_lot_per_signal`

### 2. Weighted Layering
Risk is split across multiple price levels.  
Deeper entries receive **larger lots** – start small, scale only if price moves deeper.

### 3. Pip Model
- Gold / `XAUUSD` → `0.1` = 1 pip  
- Forex (`EURUSD`, `GBPUSD`, etc.) → `0.0001` = 1 pip  

### 4. Conservative Overrides
- Max open positions – hard limit on concurrent setups
- Spread check – avoid excessive slippage
- Entry range grace – reject if price moved too far

### 5. Break‑Even Plus
Once price moves **X pips** in profit, stop loss moves **beyond entry** by a small buffer.  
Trade becomes *risk‑free* while retaining upside.

### 6. Partial Profit Taking
At each TP level, close a percentage (e.g. 30% at TP1, 30% at TP2, 40% runner).  
Locks in gains while keeping a runner.

---

## 🏦 REQUIREMENTS – THE PRIVATE CLIENT SETUP

- **Windows PC** (dedicated or [VPS](https://en.wikipedia.org/wiki/Virtual_private_server) recommended)
- **[Python 3.10+](https://www.python.org/downloads/)**
- **[MetaTrader 5](https://www.metatrader5.com/)** installed, logged in, and auto‑trading enabled
- **Telegram account** that is a member of the target VIP signal group

### Install Dependencies

```powershell
pip install -r requirements.txt
```
⚙️ Configuration – The Vault Keys
Copy the example configuration – never commit your secrets.
```powershell
copy config.example.py config.py
```
Then edit config.py with:
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           🔐 TELEGRAM API CREDENTIALS                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • api_id         ──  your unique application identifier                      ║
║  • api_hash       ──  secret key from my.telegram.org                         ║
║  • phone          ──  your Telegram account number (with country code)        ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              💹 MT5 GATEWAY                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • login          ──  MT5 account number                                      ║
║  • password       ──  trading account password                                ║
║  • server         ──  broker server name (e.g., "ICMarkets-Demo")             ║
║  • path           ──  full path to terminal64.exe                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ⚖️ RISK PARAMETERS                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • risk_percent           ──  % of balance per signal (e.g., 1.0)             ║
║  • max_lot_per_signal     ──  absolute cap on total lot size                  ║
║  • max_open_trades        ──  maximum concurrent positions                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ⏱️ SESSION CONTROLS                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • session_start          ──  London/New York open hour (UTC)                 ║
║  • session_end            ──  close hour (UTC)                                ║
║  • max_spread             ──  reject trades if spread > this (in points)      ║
║  • breakeven_buffer       ──  pips beyond entry before moving SL              ║
║  • tp_partial_percentages ──  list: e.g., [30, 30, 40] for TP1, TP2, runner   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              📰 NEWS BLACKOUT (OPTIONAL)                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • news_blackout_windows ──  list of (start_utc, end_utc) tuples              ║
║                              e.g., [("13:30", "15:00"), ("18:00", "19:30")]   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
⚠️ The following files are automatically ignored by .gitignore – keep them private:
config.py, *.session, bot.log, bot_trades.db

🧾 Audit Ledger (SQLite)
All signals, decisions, orders, and errors are logged in bot_trades.db.
A complete immutable record – essential for post‑trade review and capital accountability.

▶️ Launching the Engine
First, verify MT5 can see XAUUSD (or your preferred instruments):

```powershell
python check_mt5.py
Then start the execution suite:
```
```powershell
python bot.py
```
💎 Safety & Stewardship

This system can place real orders on a live MT5 account.
Always test first on a demo account for at least two weeks.
Trading carries risk of total capital loss. Automation reduces emotional errors but does not eliminate market risk.
Monitor the bot regularly – no system is set‑and‑forget.

📜 License & Heritage

Proprietary – for private use only.
Designed for sophisticated market participants who understand layered execution and risk budgeting.
```
“The four most expensive words in investing are ‘this time is different.’”
```
— Sir John Templeton
