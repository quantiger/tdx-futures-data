import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import time
import os

tq.initialize(__file__)

field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
start_date = '20250701'
end_date = '20260503'

os.makedirs('futures_5m', exist_ok=True)

contracts = [f.replace('.csv', '') for f in os.listdir('futures_data') if f.endswith('.csv')]
print(f"1分钟合约: {len(contracts)} 个")

collected = set(f.replace('.csv', '') for f in os.listdir('futures_5m') if f.endswith('.csv'))
print(f"已采集5m: {len(collected)} 个")

missing = [c for c in contracts if c not in collected]
print(f"缺失: {len(missing)} 个")

total = len(missing)
for i, code in enumerate(missing):
    print(f"\n[{i+1}/{total}] {code}...", end=" ", flush=True)
    
    all_data = []
    for batch in range(24):
        result = tq.get_market_data(
            field_list=field_list,
            stock_list=[code],
            start_time=start_date,
            end_time=end_date,
            period='5m',
            dividend_type='none',
            count=24000
        )
        
        if not result or 'Open' not in result:
            break
        
        dfs = []
        for field in field_list:
            if field in result:
                df = result[field].copy()
                if code in df.columns:
                    df.columns = [field]
                    dfs.append(df)
        
        if not dfs:
            break
        
        merged = dfs[0]
        for df in dfs[1:]:
            merged = merged.join(df, how='outer')
        
        merged = merged.reset_index()
        count = len(merged)
        all_data.append(merged)
        
        if count < 24000:
            break
        
        time.sleep(0.3)
    
    if not all_data:
        print("无数据")
        continue
    
    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.drop_duplicates()
    combined = combined.sort_values('index')
    combined = combined.reset_index(drop=True)
    combined.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest']
    combined['code'] = code
    
    print(f"{len(combined)} 条")
    combined.to_csv(f'futures_5m/{code}.csv', index=False)
    time.sleep(0.3)

tq.close()
print("\n完成!")