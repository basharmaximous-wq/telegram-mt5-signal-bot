"""
Example configuration for the Telegram -> MT5 Signal Bot.

Copy this file to config.py and fill in your private credentials locally.
Never commit config.py to GitHub.
"""

CONFIG = {
    # Telegram API credentials from https://my.telegram.org
    "api_id": 12345678,
    "api_hash": "YOUR_TELEGRAM_API_HASH",
    "phone": "+491234567890",
    "vip_group": "Your VIP Group Name or Chat ID",

    # MetaTrader 5 login
    "mt5_login": 12345678,
    "mt5_password": "YOUR_MT5_PASSWORD",
    "mt5_server": "YourBroker-Demo",

    # Risk profile
    "max_lot_per_signal": 0.10,
    "max_open_signals": 3,
    "risk_per_trade_pct": 1.0,

    # Entry discipline
    "grace_pips": 30,
    "num_entries": 3,
    "weighted_layering": True,
    "pending_alert_timeout_s": 180,

    # Session filter, UTC hours
    "session_start_utc": 7,
    "session_end_utc": 21,

    # Allowed instruments
    "allowed_pairs": [
        "XAUUSD", "EURUSD", "GBPUSD",
        "GBPJPY", "USDJPY", "USDCHF",
        "AUDUSD", "NZDUSD", "USDCAD",
    ],

    # Trade management
    "tp1_partial_close": 0.33,
    "tp2_partial_close": 0.33,
    "be_trigger_pips": 10,
    "be_plus_pips": 1,
    "manual_take_profit_close_fraction": 0.50,
    "close_on_setup_failed": False,
    "monitor_interval_s": 5,

    # Optional manual red-news blackout windows in UTC
    "news_blackout_windows_utc": [],
}
