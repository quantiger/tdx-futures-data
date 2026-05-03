import sys
import os
import time
import json
from datetime import datetime, timedelta

import config

TDX_PATH = os.path.join(config.TDX_PLUGIN_PATH.replace('/', os.sep).replace('\\', os.sep))
if os.path.exists(TDX_PATH):
    sys.path.insert(0, TDX_PATH)
    from tqcenter import tq
else:
    raise ImportError(f"TDX路径不存在: {TDX_PATH}")


class TdxFetcher:
    def __init__(self):
        self.tq = tq
        self._initialize()

    def _initialize(self):
        self.tq.initialize(__file__)
        print(f"[{datetime.now()}] TDX接口初始化完成")

    def get_main_contracts(self, exchange):
        futures = config.FUTURES_CODES.get(exchange, [])
        suffix = config.EXCHANGES[exchange]['suffix']
        return [f"{code}L8{suffix}" for code in futures]

    def get_all_contracts(self):
        contracts = {}
        for exchange in config.EXCHANGES:
            contracts[exchange] = self.get_main_contracts(exchange)
        return contracts

    def get_kline_data(self, codes, start_date, end_date, period='1m'):
        start_time = start_date.replace('-', '')
        end_time = end_date.replace('-', '')

        all_data = {}

        for code in codes:
            try:
                batches = self._fetch_with_batches(code, start_time, end_time, period)
                if batches:
                    all_data[code] = batches
                    print(f"  {code}: 获取 {len(batches)} 条数据")
                else:
                    print(f"  {code}: 无数据")
            except Exception as e:
                print(f"  {code}: 获取失败 - {e}")

            time.sleep(0.5)

        return all_data

    def _fetch_with_batches(self, code, start_time, end_time, period):
        import pandas as pd
        
        records = []
        current_start = start_time

        while True:
            result = self.tq.get_market_data(
                field_list=['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'VolInStock'],
                stock_list=[code],
                start_time=current_start,
                end_time=end_time,
                period=period,
                dividend_type='none',
                fill_data=False,
                count=config.MAX_RECORDS_PER_BATCH
            )

            if result is None or len(result) == 0:
                break

            df_dict = result
            
            for field in ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']:
                if field not in df_dict:
                    continue
                    
                df = df_dict[field]
                if df is None or df.empty:
                    continue
                
                if code not in df.columns:
                    continue
                
                series = df[code]
                for dt, val in series.items():
                    if pd.isna(val):
                        continue
                    existing = next((r for r in records if r.get('datetime') == str(dt)), None)
                    if existing is None:
                        records.append({
                            'datetime': str(dt),
                            'code': code,
                        })
                        existing = records[-1]
                    
                    field_map = {
                        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                        'Volume': 'volume', 'Amount': 'amount', 'VolInStock': 'open_interest'
                    }
                    if field in field_map:
                        existing[field_map[field]] = val

            if len(records) == 0:
                break

            if len(records) < config.MAX_RECORDS_PER_BATCH:
                break

            if records:
                last_dt = records[-1].get('datetime', '')
                if last_dt:
                    current_start = self._next_day(str(last_dt))
                else:
                    break
            else:
                break

        return records

    def _next_day(self, datetime_str):
        if len(datetime_str) >= 8:
            date_part = datetime_str[:8]
            try:
                dt = datetime.strptime(date_part, '%Y%m%d')
                next_dt = dt + timedelta(days=1)
                return next_dt.strftime('%Y%m%d')
            except:
                pass
        return datetime_str

    def refresh_cache(self, markets=['QH']):
        result = self.tq.refresh_cache(market='QH')
        print(f"[{datetime.now()}] 刷新行情缓存: {result}")
        return result

    def refresh_kline(self, codes, period='1m'):
        result = self.tq.refresh_kline(stock_list=codes, period=period)
        print(f"[{datetime.now()}] 刷新K线缓存: {result}")
        return result

    def close(self):
        try:
            self.tq.close()
        except:
            pass


if __name__ == '__main__':
    fetcher = TdxFetcher()
    contracts = fetcher.get_all_contracts()

    print("主力合约列表:")
    for exchange, codes in contracts.items():
        print(f"  {exchange}: {len(codes)} 个")

    print("\n测试获取数据...")
    test_data = fetcher.get_kline_data(['IFL8.CFF'], '20250707', '20250710', '1m')
    print(f"测试数据: {test_data}")

    fetcher.close()