import pandas as pd
import os

os.makedirs('futures_weekly', exist_ok=True)

files = [f for f in os.listdir('futures_daily') if f.endswith('.csv')]
print(f"源数据: {len(files)} 个日线文件")

for i, fname in enumerate(files):
    code = fname.replace('.csv', '')
    print(f"[{i+1}/{len(files)}] {code}", end=" ", flush=True)
    
    df = pd.read_csv(f'futures_daily/{fname}')
    if 'datetime' not in df.columns:
        print(" skip")
        continue
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()
    
    ohlc = df.resample('W').agg({
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
    
    ohlc.to_csv(f'futures_weekly/{code}.csv', index=False)
    print(" OK")

print("\n完成!")