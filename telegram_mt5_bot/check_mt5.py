"""
Quick MT5 connection and XAUUSD tick check.
Run with: python check_mt5.py
"""

import MetaTrader5 as mt5

from config import CONFIG


def main():
    ok = mt5.initialize(
        login=CONFIG["mt5_login"],
        password=CONFIG["mt5_password"],
        server=CONFIG["mt5_server"],
    )
    if not ok:
        print("MT5 initialize failed:", mt5.last_error())
        return

    symbol = "XAUUSD"
    info = mt5.symbol_info(symbol)
    print("symbol_info:", info)
    if info is None:
        print("XAUUSD was not found. Check the exact symbol name in Market Watch.")
        mt5.shutdown()
        return

    if not info.visible:
        print("XAUUSD is hidden. Selecting it now...")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select failed:", mt5.last_error())
            mt5.shutdown()
            return

    tick = mt5.symbol_info_tick(symbol)
    print("tick:", tick)
    if tick is None:
        print("No live tick. Make sure MT5 is logged in and prices are moving.")
    else:
        print(f"OK: XAUUSD bid={tick.bid} ask={tick.ask}")

    mt5.shutdown()


if __name__ == "__main__":
    main()
