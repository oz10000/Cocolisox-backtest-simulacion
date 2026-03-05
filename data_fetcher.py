# data_fetcher.py
import requests
import time
from datetime import datetime, timedelta
import pandas as pd
from config import KUCOIN_BASE_URL, CANDLES_ENDPOINT, TIMEFRAME

def fetch_klines(symbol, start_at=None, end_at=None, limit=1500):
    """
    Descarga velas de KuCoin.
    :param symbol: str, ej. 'BTC-USDT'
    :param start_at: timestamp en segundos (opcional)
    :param end_at: timestamp en segundos (opcional)
    :param limit: máximo de velas por petición (KuCoin max 1500)
    :return: DataFrame con columnas: time, open, close, high, low, volume, turnover
    """
    params = {
        'symbol': symbol,
        'type': TIMEFRAME,
        'limit': limit
    }
    if start_at:
        params['startAt'] = start_at
    if end_at:
        params['endAt'] = end_at

    url = KUCOIN_BASE_URL + CANDLES_ENDPOINT
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('code') != '200000':
        raise Exception(f"Error fetching data: {data}")

    candles = data['data']
    # KuCoin devuelve: [time, open, close, high, low, volume, turnover]
    df = pd.DataFrame(candles, columns=['time', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
    # Convertir tipos
    df['time'] = pd.to_numeric(df['time'])
    df['open'] = pd.to_numeric(df['open'])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['turnover'] = pd.to_numeric(df['turnover'])
    # Ordenar por tiempo ascendente
    df = df.sort_values('time').reset_index(drop=True)
    return df

def fetch_historical_data(symbol, start_date, end_date):
    """
    Descarga datos históricos en un rango de fechas manejando paginación.
    :param symbol: str
    :param start_date: datetime
    :param end_date: datetime
    :return: DataFrame concatenado
    """
    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    all_dfs = []
    current_end = end_ts
    while current_end > start_ts:
        df = fetch_klines(symbol, end_at=current_end, limit=1500)
        if df.empty:
            break
        all_dfs.append(df)
        first_time = df['time'].iloc[0]
        if first_time <= start_ts:
            break
        current_end = first_time - 1
    if all_dfs:
        full_df = pd.concat(all_dfs, ignore_index=True)
        full_df = full_df.sort_values('time').drop_duplicates(subset='time').reset_index(drop=True)
        full_df = full_df[(full_df['time'] >= start_ts) & (full_df['time'] <= end_ts)]
        return full_df
    else:
        return pd.DataFrame()

def fetch_current_price(symbol):
    """Obtiene el último precio (última vela) para un símbolo."""
    df = fetch_klines(symbol, limit=1)
    if not df.empty:
        return df['close'].iloc[-1]
    return None
