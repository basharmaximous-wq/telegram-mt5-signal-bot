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
║                           🔐 TELEGRAM API CREDENTIALS                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • api_id         ──  your unique application identifier                      ║
║  • api_hash       ──  secret key from my.telegram.org                         ║
║  • phone          ──  your Telegram account number (with country code)        ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              💹 MT5 GATEWAY                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • login          ──  MT5 account number                                      ║
║  • password       ──  trading account password                                ║
║  • server         ──  broker server name (e.g., "ICMarkets-Demo")             ║
║  • path           ──  full path to terminal64.exe                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ⚖️ RISK PARAMETERS                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • risk_percent           ──  % of balance per signal (e.g., 1.0)             ║
║  • max_lot_per_signal     ──  absolute cap on total lot size                  ║
║  • max_open_trades        ──  maximum concurrent positions                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ⏱️ SESSION CONTROLS                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • session_start          ──  London/New York open hour (UTC)                 ║
║  • session_end            ──  close hour (UTC)                                ║
║  • max_spread             ──  reject trades if spread > this (in points)      ║
║  • breakeven_buffer       ──  pips beyond entry before moving SL              ║
║  • tp_partial_percentages ──  list: e.g., [30, 30, 40] for TP1, TP2, runner   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              📰 NEWS BLACKOUT (OPTIONAL)                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • news_blackout_windows ──  list of (start_utc, end_utc) tuples              ║
║                              e.g., [("13:30", "15:00"), ("18:00", "19:30")]   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
```
This **vault‑style ASCII box** method is:

- **Huge** – spans full width, clearly separated sections
- **Professional** – reminiscent of terminal‑based financial dashboards
- **GitHub‑safe** – uses monospaced code block with box‑drawing characters
- **Easy to read** – each parameter on its own line with a description

If you prefer a more **minimal but still large** approach, I can also provide a version with big emoji headers and indented bullet lists. Let me know.
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
```
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

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=500&color=A855F7&background=0B0014&center=true&vCenter=true&width=700&height=80&lines=تيليغرام+%E2%9E%9C+MT5;طبقات+مرجحة;بروتوكول+المخاطر+أولاً;⚖️+محرك+المخاطر+نشط" alt="Typing SVG" />
</p>

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/Python-3.10%2B-8A2BE2?style=for-the-badge&logo=python&logoColor=white&labelColor=0B0014" /></a>
  <a href="https://www.metatrader5.com/"><img src="https://img.shields.io/badge/MT5-7E22CE?style=for-the-badge&logo=metatrader5&logoColor=white&labelColor=0B0014" /></a>
  <a href="https://my.telegram.org/"><img src="https://img.shields.io/badge/Telegram-API-D8B4FE?style=for-the-badge&logo=telegram&logoColor=white&labelColor=0B0014" /></a>
</p>

<p align="center">
  <i>"الحظ يحالف المنضبطين. المخاطرة لا تُؤخذ — بل تُوزَّع."</i>
</p>

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&height=2&width=800&text=&fontColor=fff&animation=twinkling" />
</p>

## 🏛️ الملخص التنفيذي – خزينة الإشارات

محرك تنفيذ **احترافي مخصص** يربط مجموعة VIP خاصة على [تيليغرام](https://telegram.org/) بـ [MetaTrader 5](https://www.metatrader5.com/).  
مصمم لتدفق إشارات **ثنائي المرحلة** — دخول فوري يتبعه هيكل كامل لـ SL/TP.  
يعمل كـ **مكتب تداول عائلي خاص**:

- 🤫 يستمع في صمت
- 🛡️ يتحقق من الإشارات وفق إطار قواعد محافظ
- ⚖️ يوزع الانكشاف عبر **دخولات مرجحة وطبقية**
- 💰 يدير جني الأرباح الجزئي، ونقطة التعادل، وأوامر التجاوز اليدوي

> *لا تنفيذ أعمى. لا جشع. لا انكشاف غير مسيطر عليه.*

---

## ⚡ مجموعة الميزات – محرك التداول المتقدم

| الوحدة | الوصف |
|--------|--------|
| **مستمع تيليغرام** | [`Telethon`](https://docs.telethon.dev/) – يقرأ مجموعات VIP المحددة فقط |
| **تنفيذ MT5** | حزمة Python الرسمية لـ [`MetaTrader5`](https://www.metatrader5.com/en/terminal/help/algotrading/ctrade) |
| **محلل الذهب والفوركس** | يتعرف على `XAUUSD` و`GOLD` و`XAU` والأزواج الرئيسية |
| **ذاكرة الإشارة ثنائية المرحلة** | يربط SL/TP اللاحق بالدخول الفوري المعلق |
| **تطبيق الطبقات بالقواعد** | يوزع إجمالي المخاطر عبر الدخولات؛ الأعمق = حجم لوت أكبر |
| **فلتر الجلسة** | يتداول فقط خلال لندن ونيويورك (قابل للتخصيص) |
| **حارس السبريد** | يمنع التداول إذا تجاوز السبريد الحد الأقصى |
| **حد الصفقات المفتوحة** | يمنع الإفراط في الالتزام |
| **صحة نطاق الدخول** | يرفض النطاقات الواسعة بشكل غير منطقي |
| **التحقق من SL و TP** | يضمن صحة اتجاه وقف الخسارة والأهداف |
| **مهلة انتظار الإشارة** | يغلق الدخول غير المحمي إذا لم تصل متابعة |
| **نقطة التعادل + هامش** | ينقل SL إلى ما بعد نقطة الدخول عند بلوغ هامش الربح |
| **جني الأرباح الجزئي** | يغلق نسبة قابلة للتعديل عند كل مستوى TP |
| **الإدارة اليدوية** | `breakeven` و`take some profits` و`adjust SL to 4688` |
| **نوافذ توقف أخبار** | مبنية على UTC – لا صفقات جديدة خلال التقلبات |
| **استعادة بعد إعادة التشغيل** | يعيد تحميل الصفقات المفتوحة التي يديرها البوت بعد إعادة التشغيل |
| **سجل SQLite** | سجل تدقيق غير قابل للتغيير للإشارات والصفقات والأخطاء |
| **فاحص صحة MT5** | يتحقق من الاتصال وتوفر الرموز |

---

## 🧠 إطار الحفاظ على الثروة – محرك المخاطر

هذا البوت **لا يستخدم** حجم لوت ثابتاً. إنه يحاكي **مكتب تداول خاصاً**:

### 1. التحديد القائم على المخاطر أولاً
- نسبة مخاطرة من الرصيد الحالي (مثلاً 1%)
- قياس المسافة بالنقطة من الدخول إلى SL
- **حجم اللوت = (مبلغ المخاطرة) / (مسافة النقاط × قيمة النقطة)**

> **مثال**  
> الرصيد: $5,000 | المخاطرة: 1% ← $50 على المحك  
> الذهب: دخول 4700، SL 4695 ← مسافة 50 نقطة (0.1 لكل نقطة)  
> يُحسب حجم اللوت ثم يُحدد بسقف `max_lot_per_signal`

### 2. التوزيع الطبقي المرجح
تُوزع المخاطر عبر مستويات أسعار متعددة.  
الدخولات الأعمق تحصل على **لوت أكبر** – ابدأ صغيراً، وزد الحجم فقط إذا تحرك السعر أعمق.

### 3. نموذج النقاط
- الذهب / `XAUUSD` ← `0.1` = نقطة واحدة  
- الفوركس (`EURUSD`, `GBPUSD`, ...) ← `0.0001` = نقطة واحدة  

### 4. التجاوزات المحافظة
- حد الصفقات المفتوحة – سقف صارم على الإعدادات المتزامنة
- فحص السبريد – تجنب الانزلاق المفرط
- هامش نطاق الدخول – رفض إذا تحرك السعر بعيداً جداً

### 5. نقطة التعادل المحسنة
بمجرد أن يتحرك السعر **X نقطة** في الربح، ينتقل وقف الخسارة **إلى ما بعد نقطة الدخول** بهامش صغير.  
تصبح الصفقة *بلا مخاطرة* مع الاحتفاظ بالاتجاه الصاعد.

### 6. جني الأرباح الجزئي
عند كل مستوى TP، أغلق نسبة (مثلاً 30% عند TP1، 30% عند TP2، 40% رنر).  
يحجز الأرباح مع الإبقاء على صفقة متبقية.

---

## 🏦 المتطلبات – إعداد العميل الخاص

- **كمبيوتر Windows** (مخصص أو [VPS](https://en.wikipedia.org/wiki/Virtual_private_server) مُوصى به)
- **[Python 3.10+](https://www.python.org/downloads/)**
- **[MetaTrader 5](https://www.metatrader5.com/)** مُثبَّت ومُسجَّل الدخول ومُفعَّل التداول الآلي
- **حساب تيليغرام** عضو في مجموعة إشارات VIP المستهدفة

### تثبيت المكتبات

```powershell
pip install -r requirements.txt
```

---

## ⚙️ الإعداد – مفاتيح الخزينة

انسخ ملف الإعداد المثالي — لا تحمّل أسرارك على الإنترنت.

```powershell
copy config.example.py config.py
```

ثم عدّل `config.py` بالمعلومات التالية:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        🔐 بيانات اعتماد تيليغرام API                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • api_id         ──  معرّف التطبيق الفريد الخاص بك                                   ║
║  • api_hash       ──  المفتاح السري من my.telegram.org                             ║
║  • phone          ──  رقم حساب تيليغرام (مع رمز الدولة)                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              💹 بوابة MT5                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • login          ──  رقم حساب MT5                                             ║
║  • password       ──  كلمة مرور حساب التداول                                        ║
║  • server         ──  اسم سيرفر الوسيط (مثلاً: "ICMarkets-Demo")                     ║
║  • path           ──  المسار الكامل لـ terminal64.exe                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ⚖️ معايير المخاطر                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • risk_percent           ──  % من الرصيد لكل إشارة (مثلاً: 1.0)                      ║
║  • max_lot_per_signal     ──  الحد الأقصى المطلق لإجمالي حجم اللوت                      ║
║  • max_open_trades        ──  الحد الأقصى للصفقات المتزامنة                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ⏱️ إعدادات الجلسة                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • session_start          ──  ساعة فتح جلسة لندن/نيويورك (UTC)                       ║
║  • session_end            ──  ساعة إغلاق الجلسة (UTC)                              ║
║  • max_spread             ──  رفض الصفقة إذا تجاوز السبريد هذا الحد (نقطة)                ║
║  • breakeven_buffer       ──  نقاط بعد الدخول لنقل SL                               ║
║  • tp_partial_percentages ──  قائمة مثل: [30, 30, 40] لـ TP1، TP2، رنر              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║                          📰 نوافذ توقف الأخبار (اختياري)                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  • news_blackout_windows  ──  قائمة من أزواج (start_utc, end_utc)                 ║
║                               مثلاً: [("13:30", "15:00"), ("18:00", "19:30")] ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

> ⚠️ الملفات التالية يتجاهلها `.gitignore` تلقائياً – احتفظ بها سرية:  
> `config.py` &nbsp;|&nbsp; `*.session` &nbsp;|&nbsp; `bot.log` &nbsp;|&nbsp; `bot_trades.db`

---

## 🧾 سجل التدقيق (SQLite)

جميع الإشارات والقرارات والأوامر والأخطاء مسجلة في `bot_trades.db`.  
سجل كامل غير قابل للتغيير — ضروري لمراجعة ما بعد التداول ومساءلة رأس المال.

---

## ▶️ تشغيل المحرك

أولاً، تأكد من أن MT5 يستطيع رؤية XAUUSD (أو الأدوات المفضلة لديك):

```powershell
python check_mt5.py
```

ثم ابدأ منظومة التنفيذ:

```powershell
python bot.py
```

---

## 💎 السلامة والأمانة

هذا النظام قادر على وضع أوامر حقيقية على حساب MT5 حي.  
**اختبر دائماً على حساب تجريبي لمدة أسبوعين على الأقل.**  
التداول ينطوي على خطر خسارة رأس المال بالكامل. الأتمتة تقلل الأخطاء العاطفية لكنها لا تُلغي مخاطر السوق.  
راقب البوت بانتظام — لا يوجد نظام يعمل من تلقاء نفسه إلى الأبد.

---

## 📜 الترخيص والميراث

ملكية خاصة — للاستخدام الشخصي فقط.  
مصمم لمشاركي السوق المتمرسين الذين يفهمون التنفيذ الطبقي وميزانية المخاطر.

> *"أغلى كلمات في الاستثمار هي: 'هذه المرة مختلفة'."*  
> —  جون تمبلتون
