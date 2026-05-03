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
field_map = {'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
            'Volume': 'volume', 'Amount': 'amount', 'VolInStock': 'open_interest'}

all_records = []
batch = 0
current_start = start_date

while batch < 20:
    print(f"  第{batch+1}批...", end=" ", flush=True)
    
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
        print("无数据")
        break
    
    df = result['Open']
    rows = len(df)
    print(f"{rows}条", end=" ", flush=True)
    
    records = []
    for field in field_list:
        if field not in result:
            continue
        df = result[field]
        if code not in df.columns:
            continue
        series = df[code]
        for dt, val in series.items():
            if pd.isna(val):
                continue
            existing = next((r for r in records if r.get('datetime') == str(dt)), None)
            if existing is None:
                records.append({'datetime': str(dt), 'code': code})
                existing = records[-1]
            if field in field_map:
                existing[field_map[field]] = val
    
    all_records.extend(records)
    print(f"总计{len(all_records)}")
    
    if rows < 24000:
        break
    
    # 移动到下一天
    if records:
        last_dt = records[-1].get('datetime', '')
        if last_dt:
            try:
                from datetime import datetime, timedelta
                dt = datetime.strptime(last_dt[:10], '%Y-%m-%d')
                next_dt = dt + timedelta(days=1)
                current_start = next_dt.strftime('%Y%m%d')
            except:
                pass
    
    time.sleep(0.5)
    batch += 1

print(f"\n总计获取 {len(all_records)} 条数据")

if all_records:
    df = pd.DataFrame(all_records)
    df.to_csv(f'{code}.csv', index=False)
    print(f"已保存到 {code}.csv")
    print(df.head(3))

tq.close()
print("完成")