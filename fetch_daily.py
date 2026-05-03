import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import time
import config
import os

tq.initialize(__file__)
print("初始化成功")

tq.refresh_cache(market='QH')
time.sleep(1)

# 日线字段
field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
start_date = '20150101'
end_date = '20260503'

# 获取所有合约
all_contracts = []
for exchange in config.EXCHANGES:
    futures = config.FUTURES_CODES.get(exchange, [])
    suffix = config.EXCHANGES[exchange]['suffix']
    for code in futures:
        all_contracts.append(f"{code}L8{suffix}")

print(f"共 {len(all_contracts)} 个合约")
print(f"时间范围: {start_date} ~ {end_date}")

output_dir = 'futures_daily'
os.makedirs(output_dir, exist_ok=True)

total_contracts = len(all_contracts)
for i, code in enumerate(all_contracts):
    print(f"\n[{i+1}/{total_contracts}] {code}...", end=" ", flush=True)
    
    file_path = os.path.join(output_dir, f"{code}.csv")
    if os.path.exists(file_path):
        print("已存在，跳过")
        continue
    
    result = tq.get_market_data(
        field_list=field_list,
        stock_list=[code],
        start_time=start_date,
        end_time=end_date,
        period='1d',
        dividend_type='none',
        count=5000
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
        print("无有效数据")
        continue
    
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.join(df, how='outer')
    
    merged = merged.reset_index()
    merged.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest']
    merged['code'] = code
    
    rows = len(merged)
    print(f"{rows} 条")
    
    merged.to_csv(file_path, index=False)
    time.sleep(0.3)

tq.close()
print("\n完成!")