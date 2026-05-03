import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd

tq.initialize(__file__)
tq.refresh_cache(market='QH')

code = 'IFL8.CFF'
result = tq.get_market_data(
    field_list=['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock'],
    stock_list=[code],
    start_time='20250707',
    end_time='20250715',
    period='1m',
    dividend_type='none',
    count=100
)

print("Result keys:", result.keys())
for k, v in result.items():
    print(f"\n{k}:")
    if isinstance(v, pd.DataFrame):
        print(f"  columns: {v.columns.tolist()}")
        print(f"  shape: {v.shape}")
        if code in v.columns:
            print(f"  data sample: {v[code].head(3).to_dict()}")

tq.close()