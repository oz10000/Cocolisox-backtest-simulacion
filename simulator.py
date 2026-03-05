# simulator.py
import time
from datetime import datetime
import pandas as pd
from data_fetcher import fetch_klines, fetch_current_price
from strategy import get_signal_on_last
from aeie_trailing_stop import AEIETrailingStop
from config import ASSETS, LIVE_INTERVAL, AEIE_INTERVAL, TP, SL, INITIAL_CAPITAL
import threading

class Position:
    def __init__(self, symbol, entry_price, direction):
        self.symbol = symbol
        self.entry_price = entry_price
        self.direction = direction
        self.entry_time = datetime.now()
        if direction == 'LONG':
            self.sl_price = entry_price * (1 - SL)
            self.tp_price = entry_price * (1 + TP)
        else:
            self.sl_price = entry_price * (1 + SL)
            self.tp_price = entry_price * (1 - TP)
        self.aeie = AEIETrailingStop(entry_price, direction, self.sl_price)
        self.exit_price = None
        self.exit_time = None
        self.profit_pct = None
        self.closed = False

    def update_aeie(self, current_price):
        new_stop = self.aeie.update(current_price)
        if new_stop != self.sl_price:
            self.sl_price = new_stop
            print(f"AEIE UPDATE: {self.symbol} nuevo SL={self.sl_price:.2f}")
        if self.aeie.check_stop(current_price):
            self.close(current_price, 'AEIE')
            return True
        if self.direction == 'LONG' and current_price >= self.tp_price:
            self.close(current_price, 'TP')
            return True
        if self.direction == 'SHORT' and current_price <= self.tp_price:
            self.close(current_price, 'TP')
            return True
        return False

    def close(self, price, reason):
        self.exit_price = price
        self.exit_time = datetime.now()
        if self.direction == 'LONG':
            self.profit_pct = (price - self.entry_price) / self.entry_price
        else:
            self.profit_pct = (self.entry_price - price) / self.entry_price
        self.closed = True
        print(f"CLOSE TRADE: {self.symbol} {self.direction} salida={price:.2f} razón={reason} profit={self.profit_pct*100:.2f}%")

class Simulator:
    def __init__(self):
        self.capital = INITIAL_CAPITAL
        self.positions = {}
        self.running = True

    def run(self):
        signal_thread = threading.Thread(target=self._signal_loop)
        signal_thread.daemon = True
        signal_thread.start()

        aeie_thread = threading.Thread(target=self._aeie_loop)
        aeie_thread.daemon = True
        aeie_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("Simulación detenida.")

    def _signal_loop(self):
        while self.running:
            self.check_signals()
            time.sleep(LIVE_INTERVAL)

    def _aeie_loop(self):
        while self.running:
            self.update_aeie()
            time.sleep(AEIE_INTERVAL)

    def check_signals(self):
        for symbol in ASSETS:
            if symbol in self.positions and not self.positions[symbol].closed:
                continue
            df = fetch_klines(symbol, limit=100)
            if df.empty:
                continue
            signal = get_signal_on_last(df)
            if signal:
                entry_price = df['close'].iloc[-1]
                print(f"SIGNAL DETECTED: {symbol} {signal} a {entry_price}")
                self.open_trade(symbol, entry_price, signal)

    def open_trade(self, symbol, entry_price, direction):
        position = Position(symbol, entry_price, direction)
        self.positions[symbol] = position
        print(f"OPEN TRADE: {symbol} {direction} entrada={entry_price:.2f} SL={position.sl_price:.2f} TP={position.tp_price:.2f}")

    def update_aeie(self):
        for symbol, pos in list(self.positions.items()):
            if pos.closed:
                del self.positions[symbol]
                continue
            current_price = fetch_current_price(symbol)
            if current_price is None:
                continue
            closed = pos.update_aeie(current_price)
            if closed:
                self.capital = self.capital * (1 + pos.profit_pct)
                print(f"CAPITAL: {self.capital:.2f}")
