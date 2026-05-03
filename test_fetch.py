import sys
import os

sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import time

tq.initialize(__file__)
print("初始化成功")

tq.refresh_cache(market='QH')
print("缓存刷新成功")
time.sleep(5)

result = tq.get_market_data(
    field_list=['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock'],
    stock_list=['IFL8.CFF'],
    start_time='20250707',
    end_time='20250710',
    period='1m',
    dividend_type='none',
    count=100
)

print(f"\nResult keys: {result.keys()}")

for k, v in result.items():
    if isinstance(v, pd.DataFrame):
        print(f"\n{k}:")
        print(f"  Columns: {v.columns.tolist()}")
        print(f"  Shape: {v.shape}")
        if 'IFL8.CFF' in v.columns:
            print(f"  Data sample:")
            print(v['IFL8.CFF'].head(5))

tq.close()
print("\n完成")