# backtest.py
import pandas as pd
from data_fetcher import fetch_historical_data
from strategy import calculate_deviation
from config import TP, SL, TIMEOUT_BARS, ASSETS, INITIAL_CAPITAL
from metrics import compute_metrics
import numpy as np
from datetime import datetime, timedelta

class Trade:
    def __init__(self, symbol, entry_time, entry_price, direction):
        self.symbol = symbol
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.direction = direction  # 'LONG' o 'SHORT'
        self.exit_time = None
        self.exit_price = None
        self.profit_pct = None
        self.closed_by = None  # 'TP', 'SL', 'TIMEOUT'

def run_backtest(start_date, end_date):
    """
    Ejecuta backtest para todos los activos en el rango de fechas.
    Retorna lista de trades y capital final.
    """
    all_trades = []
    capital = INITIAL_CAPITAL
    for symbol in ASSETS:
        print(f"Descargando datos para {symbol}...")
        df = fetch_historical_data(symbol, start_date, end_date)
        if df.empty:
            print(f"No hay datos para {symbol}")
            continue
        df = calculate_deviation(df)
        trades = backtest_symbol(df, symbol)
        all_trades.extend(trades)
        for t in trades:
            capital = capital * (1 + t.profit_pct)

    metrics = compute_metrics(all_trades, capital)
    return all_trades, metrics

def backtest_symbol(df, symbol):
    """
    Backtest para un símbolo individual.
    df debe tener columnas: time, open, high, low, close, deviation
    """
    trades = []
    i = 0
    while i < len(df) - TIMEOUT_BARS:
        row = df.iloc[i]
        dev = row['deviation']
        if dev > 0.003:
            direction = 'SHORT'
        elif dev < -0.003:
            direction = 'LONG'
        else:
            i += 1
            continue

        entry_price = row['close']
        entry_time = row['time']

        if direction == 'LONG':
            tp_price = entry_price * (1 + TP)
            sl_price = entry_price * (1 - SL)
        else:
            tp_price = entry_price * (1 - TP)
            sl_price = entry_price * (1 + SL)

        closed = False
        for j in range(1, TIMEOUT_BARS + 1):
            if i + j >= len(df):
                break
            next_row = df.iloc[i + j]
            high = next_row['high']
            low = next_row['low']

            if direction == 'LONG':
                if low <= sl_price:
                    exit_price = sl_price
                    exit_time = next_row['time']
                    profit_pct = -SL
                    closed_by = 'SL'
                    closed = True
                    break
                if high >= tp_price:
                    exit_price = tp_price
                    exit_time = next_row['time']
                    profit_pct = TP
                    closed_by = 'TP'
                    closed = True
                    break
            else:
                if high >= sl_price:
                    exit_price = sl_price
                    exit_time = next_row['time']
                    profit_pct = -SL
                    closed_by = 'SL'
                    closed = True
                    break
                if low <= tp_price:
                    exit_price = tp_price
                    exit_time = next_row['time']
                    profit_pct = TP
                    closed_by = 'TP'
                    closed = True
                    break

        if not closed:
            exit_row = df.iloc[i + TIMEOUT_BARS]
            exit_price = exit_row['close']
            exit_time = exit_row['time']
            if direction == 'LONG':
                profit_pct = (exit_price - entry_price) / entry_price
            else:
                profit_pct = (entry_price - exit_price) / entry_price
            closed_by = 'TIMEOUT'

        trade = Trade(symbol, entry_time, entry_price, direction)
        trade.exit_time = exit_time
        trade.exit_price = exit_price
        trade.profit_pct = profit_pct
        trade.closed_by = closed_by
        trades.append(trade)

        i += j + 1

    return trades
