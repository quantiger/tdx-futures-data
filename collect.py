import sys
import os
import time

sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import config
from src.storage import Storage
import time as time_module

class SimpleFetcher:
    def get_main_contracts(self, exchange):
        futures = config.FUTURES_CODES.get(exchange, [])
        suffix = config.EXCHANGES[exchange]['suffix']
        return [f"{code}L8{suffix}" for code in futures]

fetcher = SimpleFetcher()
storage = Storage()

tq.initialize(__file__)
print("初始化成功")

tq.refresh_cache(market='QH')
time.sleep(1)

# 获取所有合约并刷新K线缓存
all_contracts = []
for exchange in config.EXCHANGES:
    all_contracts.extend(fetcher.get_main_contracts(exchange))
tq.refresh_kline(stock_list=all_contracts, period='1m')
time.sleep(2)

exchanges = list(config.EXCHANGES.keys())
start_date = '20250707'
end_date = '20260503'
print(f"时间范围: {start_date} ~ {end_date}")
print("注意: 需要客户端已下载该时间范围的盘后数据")

field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
field_map = {'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
            'Volume': 'volume', 'Amount': 'amount', 'VolInStock': 'open_interest'}

all_data = {}

for exchange in exchanges:
    print(f"\n[{exchange}] 开始获取...")
    contracts = fetcher.get_main_contracts(exchange)
    print(f"  合约数量: {len(contracts)}")
    
    exchange_data = {}
    
    for code in contracts:
        try:
            print(f"  正在获取 {code}...", end=" ", flush=True)
            
            records = []
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
            
            df = result['Open']
            rows = len(df)
            print(f"[{rows}条]", end=" ", flush=True)
            
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
            
            if records:
                exchange_data[code] = records
                print(f"OK")
            else:
                print(f"无数据")
                
        except Exception as e:
            print(f"失败: {e}")
        
        time.sleep(0.3)
    
    all_data[exchange] = exchange_data
    
    total = sum(len(v) for v in exchange_data.values())
    print(f"  {exchange} 小计: {total} 条")

print("\n保存数据...")
storage.save_kline_data(all_data, '1m')

tq.close()

print("\n最终统计:")
stats = storage.get_exchange_stats('1m')
for ex, s in stats.items():
    print(f"  {ex}: {s['records']} 条, {s['codes']} 个合约")