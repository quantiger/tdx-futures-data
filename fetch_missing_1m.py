import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import time
import os

tq.initialize(__file__)

field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
start_date = '20250707'
end_date = '20260503'

futures = tq.get_stock_list('92', list_type=1)
print(f"主力合约: {len(futures)} 个")

os.makedirs('futures_data', exist_ok=True)

collected = set(f.replace('.csv', '') for f in os.listdir('futures_data') if f.endswith('.csv'))
print(f"已采集: {len(collected)} 个")

missing = []
for f in futures:
    code = f['Code']
    suffix = '.' + code.split('.')[1]
    base = code.split('.')[0][:-4] + 'L8' + suffix
    if base not in collected:
        missing.append((base, code))

print(f"缺失: {len(missing)} 个")

total = len(missing)
for i, (code, orig) in enumerate(missing):
    if os.path.exists(f'futures_data/{code}.csv'):
        continue
    print(f"\n[{i+1}/{total}] {code}...", end=" ", flush=True)
    
    result = tq.get_market_data(
        field_list=field_list,
        stock_list=[code],
        start_time=start_date,
        end_time=end_date,
        period='1m',
        dividend_type='none',
        count=24000
    )
    
    if not result or 'Open' not in result:
        print("无数据")
        continue
    
    dfs = []
    for field in field_list:
        if field in result:
            df = result[field].copy()
            if code in df.columns:
                df.columns = [field]
                dfs.append(df)
    
    if not dfs:
        print("失败")
        continue
    
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.join(df, how='outer')
    
    merged = merged.reset_index()
    merged.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest']
    merged['code'] = code
    
    print(f"{len(merged)} 条")
    merged.to_csv(f'futures_data/{code}.csv', index=False)
    time.sleep(0.3)

tq.close()
print("\n完成!")