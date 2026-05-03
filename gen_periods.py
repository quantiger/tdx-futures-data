import pandas as pd
import os

PERIODS = {
    '10min': '10min',
    '15min': '15min', 
    '30min': '30min',
    '60min': '60min',
    '120min': '120min'
}

os.makedirs('futures_10m', exist_ok=True)
os.makedirs('futures_15m', exist_ok=True)
os.makedirs('futures_30m', exist_ok=True)
os.makedirs('futures_60m', exist_ok=True)
os.makedirs('futures_120m', exist_ok=True)

files = [f for f in os.listdir('futures_5m') if f.endswith('.csv')]
print(f"源数据: {len(files)} 个5分钟文件")

for i, fname in enumerate(files):
    code = fname.replace('.csv', '')
    print(f"[{i+1}/{len(files)}] {code}", end=" ", flush=True)
    
    df = pd.read_csv(f'futures_5m/{fname}')
    if 'datetime' not in df.columns:
        print(" skip")
        continue
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()
    
    for period_code, period_name in PERIODS.items():
        ohlc = df.resample(period_code).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum',
            'open_interest': 'last'
        })
        ohlc = ohlc.dropna()
        ohlc = ohlc.reset_index()
        ohlc['code'] = code
        
        dir_map = {
            '10min': 'futures_10m',
            '15min': 'futures_15m',
            '30min': 'futures_30m',
            '60min': 'futures_60m',
            '120min': 'futures_120m'
        }
        ohlc.to_csv(f"{dir_map[period_name]}/{code}.csv", index=False)
    
    print(" OK")

print("\n完成!")