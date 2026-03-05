# main.py
from datetime import datetime, timedelta
from backtest import run_backtest
from simulator import Simulator
from metrics import compute_metrics
import pandas as pd

def main():
    print("=== INICIANDO BOT DE TRADING ===\n")

    print("--- EJECUTANDO BACKTEST ---")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    trades, metrics = run_backtest(start_date, end_date)

    print("\n=== RESULTADOS BACKTEST ===")
    print(f"Número de trades: {metrics['num_trades']}")
    print(f"Winrate: {metrics['winrate']:.4f}")
    print(f"Expectancy: {metrics['expectancy']:.6f}")
    print(f"Profit Factor: {metrics['profit_factor']:.4f}")
    print(f"Capital final: {metrics['final_capital']:.2f}")
    print(f"Retorno total: {metrics['total_return']*100:.2f}%")
    print("===========================\n")

    if trades:
        trades_df = pd.DataFrame([{
            'symbol': t.symbol,
            'entry_time': datetime.fromtimestamp(t.entry_time).strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': datetime.fromtimestamp(t.exit_time).strftime('%Y-%m-%d %H:%M:%S'),
            'direction': t.direction,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'profit_pct': t.profit_pct,
            'closed_by': t.closed_by
        } for t in trades])
        trades_df.to_csv('backtest_trades.csv', index=False)
        print("Trades guardados en backtest_trades.csv")

    print("--- INICIANDO SIMULACIÓN EN VIVO ---")
    sim = Simulator()
    sim.run()

if __name__ == "__main__":
    main()
