import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import time

tq.initialize(__file__)
print("初始化成功")

tq.refresh_cache(market='QH')
time.sleep(1)

code = 'IFL8.CFF'
start_date = '20250707'
end_date = '20260503'

print(f"\n获取 {code} ({start_date}~{end_date})...")

field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']

all_data = []
batch = 0

while batch < 20:
    print(f"  第{batch+1}批...", end=" ", flush=True)
    
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
        break
    
    # 直接用pandas合并，不逐行查找
    dfs = []
    for field in field_list:
        if field in result:
            df = result[field].copy()
            if code in df.columns:
                df.columns = [field]
                dfs.append(df)
    
    if not dfs:
        print("无有效数据")
        break
    
    # 快速合并所有字段
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.join(df, how='outer')
    
    merged = merged.reset_index()
    merged.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest']
    merged['code'] = code
    
    rows = len(merged)
    print(f"{rows}条", end=" ", flush=True)
    
    all_data.append(merged)
    print(f"累计{sum(len(d) for d in all_data)}")
    
    if rows < 24000:
        break
    
    # 移动到下一天
    last_dt = merged['datetime'].iloc[-1]
    if pd.notna(last_dt):
        try:
            dt = pd.to_datetime(last_dt)
            next_dt = dt + pd.Timedelta(days=1)
            start_date = next_dt.strftime('%Y%m%d')
        except:
            pass
    
    batch += 1
    time.sleep(0.3)

if all_data:
    df = pd.concat(all_data, ignore_index=True)
    df = df.drop_duplicates(subset=['datetime'], keep='first')
    df = df.sort_values('datetime')
    print(f"\n总计: {len(df)} 条")
    df.to_csv(f'{code}.csv', index=False)
    print(f"保存: {code}.csv")
    print(df.head(3))
else:
    print("无数据")

tq.close()
print("完成")