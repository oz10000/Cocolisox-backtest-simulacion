# config.py
# Parámetros de la estrategia
TIMEFRAME = '3min'  # KuCoin usa '3min'
EMA_SPAN = 20
DEVIATION_THRESHOLD = 0.003
TP = 0.008  # 0.8%
SL = 0.016  # 1.6%
TIMEOUT_BARS = 50

# Activos
ASSETS = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']

# Capital inicial
INITIAL_CAPITAL = 1000.0

# Trailing stop AEIE (parámetros de ejemplo)
AEIE_TRIGGER = 0.005  # Se activa cuando el beneficio flotante alcanza 0.5%
AEIE_TRAIL = 0.002    # Trailing stop del 0.2% por debajo del máximo

# Intervalos de tiempo en segundos
LIVE_INTERVAL = 180  # 3 minutos para check de señal
AEIE_INTERVAL = 15   # 15 segundos para actualizar trailing stop

# KuCoin API endpoints
KUCOIN_BASE_URL = 'https://api.kucoin.com'
CANDLES_ENDPOINT = '/api/v1/market/candles'
