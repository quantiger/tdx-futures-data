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

field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
start_date = '20250707'
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

output_dir = 'futures_data'
os.makedirs(output_dir, exist_ok=True)

total_contracts = len(all_contracts)
for i, code in enumerate(all_contracts):
    print(f"\n[{i+1}/{total_contracts}] {code}...", end=" ", flush=True)
    
    file_path = os.path.join(output_dir, f"{code}.csv")
    if os.path.exists(file_path):
        print("已存在，跳过")
        continue
    
    all_data = []
    batch = 0
    current_start = start_date
    
    while batch < 20:
        result = tq.get_market_data(
            field_list=field_list,
            stock_list=[code],
            start_time=current_start,
            end_time=end_date,
            period='1m',
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
        merged.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest']
        merged['code'] = code
        
        rows = len(merged)
        all_data.append(merged)
        
        if rows < 24000:
            break
        
        last_dt = merged['datetime'].iloc[-1]
        if pd.notna(last_dt):
            try:
                dt = pd.to_datetime(last_dt)
                next_dt = dt + pd.Timedelta(days=1)
                current_start = next_dt.strftime('%Y%m%d')
            except:
                pass
        
        batch += 1
        time.sleep(0.2)
    
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        df = df.drop_duplicates(subset=['datetime'], keep='first')
        df = df.sort_values('datetime')
        df.to_csv(file_path, index=False)
        print(f"{len(df)} 条")
    else:
        print("无数据")
    
    time.sleep(0.3)

tq.close()
print("\n完成!")