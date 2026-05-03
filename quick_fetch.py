import sys
import os
import time

sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd

tq.initialize(__file__)
print("初始化成功")

tq.refresh_cache(market='QH')
time.sleep(2)

codes = ['IFL8.CFF']
result = tq.get_market_data(
    field_list=['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock'],
    stock_list=codes,
    start_time='20250707',
    end_time='20250715',
    period='1m',
    dividend_type='none',
    count=500
)

print(f"\n获取到数据, keys: {result.keys()}")

all_records = []

for code in codes:
    records = []
    for field in ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']:
        df = result.get(field)
        if df is None or df.empty or code not in df.columns:
            continue
        series = df[code]
        for dt, val in series.items():
            if pd.isna(val):
                continue
            existing = next((r for r in records if r.get('datetime') == str(dt)), None)
            if existing is None:
                records.append({'datetime': str(dt), 'code': code})
                existing = records[-1]
            field_map = {'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                        'Volume': 'volume', 'Amount': 'amount', 'VolInStock': 'open_interest'}
            if field in field_map:
                existing[field_map[field]] = val
    
    print(f"{code}: {len(records)} 条")
    all_records.extend(records)

print(f"\n总计: {len(all_records)} 条")

if all_records:
    import json
    print("\nSample records:")
    for r in all_records[:3]:
        print(r)

tq.close()