# metrics.py
import numpy as np

def compute_metrics(trades, final_capital):
    """
    Calcula métricas a partir de lista de trades.
    trades: lista de objetos Trade con atributo profit_pct.
    final_capital: capital final después de reinversión.
    Retorna dict con métricas.
    """
    n_trades = len(trades)
    if n_trades == 0:
        return {
            'num_trades': 0,
            'winrate': 0,
            'expectancy': 0,
            'profit_factor': 0,
            'final_capital': 0,
            'total_return': 0
        }

    profits = [t.profit_pct for t in trades]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    winrate = len(wins) / n_trades
    expectancy = np.mean(profits)

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses)) if losses else 0
    profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')

    total_return = (final_capital - 1000) / 1000

    return {
        'num_trades': n_trades,
        'winrate': winrate,
        'expectancy': expectancy,
        'profit_factor': profit_factor,
        'final_capital': final_capital,
        'total_return': total_return
    }
