<!-- 
  Ultra-Violet Trading Bot README
  Dark Mode Optimized | 3D Glowing Effects | Animated SVG Headers
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
```
⚙️ Configuration – The Vault Keys
Copy the example configuration – never commit your secrets.
```powershell
copy config.example.py config.py
```
Then edit config.py with:

.Telegram API credentials (api_id, api_hash, phone)

.MT5 login, password, server, path

.Risk parameters (risk%, max lot, max open trades)

.Session hours, spread limit, break‑even buffer, partial profit percentages

.News blackout windows (optional)

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
