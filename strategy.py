# strategy.py
import pandas as pd
import numpy as np
from config import EMA_SPAN, DEVIATION_THRESHOLD

def calculate_ema(df):
    """Añade columna EMA al DataFrame."""
    df = df.copy()
    df['EMA'] = df['close'].ewm(span=EMA_SPAN, adjust=False).mean()
    return df

def calculate_deviation(df):
    """Añade columna deviation = (close - EMA)/EMA."""
    df = calculate_ema(df)
    df['deviation'] = (df['close'] - df['EMA']) / df['EMA']
    return df

def get_signal_at_index(df, index):
    """
    Determina señal en una fila específica (basado en deviation).
    Retorna 'LONG', 'SHORT' o None.
    """
    if index >= len(df):
        return None
    df_with_dev = calculate_deviation(df)
    dev = df_with_dev.loc[index, 'deviation']
    if dev > DEVIATION_THRESHOLD:
        return 'SHORT'
    elif dev < -DEVIATION_THRESHOLD:
        return 'LONG'
    else:
        return None

def get_signal_on_last(df):
    """Señal en la última vela."""
    return get_signal_at_index(df, len(df)-1)
