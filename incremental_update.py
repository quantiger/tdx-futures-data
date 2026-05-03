import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import time
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tdx_data_dir = os.path.join(BASE_DIR, 'futures_data')

def get_latest_date(code):
    path = os.path.join(tdx_data_dir, f'{code}.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    if 'datetime' not in df.columns:
        return None
    return df['datetime'].max()

def update_1min(code, start_date, end_date):
    field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
    
    result = tq.get_market_data(
        field_list=field_list,
        stock_list=[code],
        start_time=start_date,
        end_time=end_date,
        period='1m',
        dividend_type='none',
        count=5000
    )
    
    if not result or 'Open' not in result:
        return None
    
    dfs = []
    for field in field_list:
        if field in result:
            df = result[field].copy()
            if code in df.columns:
                df.columns = [field]
                dfs.append(df)
    
    if not dfs:
        return None
    
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.join(df, how='outer')
    
    merged = merged.reset_index()
    merged.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest']
    merged['code'] = code
    
    existing_path = os.path.join(tdx_data_dir, f'{code}.csv')
    if os.path.exists(existing_path):
        existing = pd.read_csv(existing_path)
        merged = pd.concat([existing, merged], ignore_index=True)
        merged = merged.drop_duplicates(subset=['datetime'])
        merged['datetime'] = pd.to_datetime(merged['datetime'])
        merged = merged.sort_values('datetime')
        merged = merged.reset_index(drop=True)
    
    merged.to_csv(existing_path, index=False)
    return merged

def regenerate_periods(code):
    source_path = os.path.join(tdx_data_dir, f'{code}.csv')
    if not os.path.exists(source_path):
        return
    
    df = pd.read_csv(source_path)
    if 'datetime' not in df.columns:
        return
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()
    
    period_map = {
        '5min': ('5min', 'futures_5m'),
        '10min': ('10min', 'futures_10m'),
        '15min': ('15min', 'futures_15m'),
        '30min': ('30min', 'futures_30m'),
        '60min': ('60min', 'futures_60m'),
        '120min': ('120min', 'futures_120m')
    }
    
    for period_name, (period_code, out_dir) in period_map.items():
        ohlc = df.resample(period_code).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum',
            'open_interest': 'last'
        })
        ohlc = ohlc.dropna()
        ohlc = ohlc.reset_index()
        ohlc['code'] = code
        ohlc.to_csv(f'{out_dir}/{code}.csv', index=False)

def regenerate_weekly(code):
    source_path = os.path.join('futures_daily', f'{code}.csv')
    if not os.path.exists(source_path):
        return
    
    df = pd.read_csv(source_path)
    if 'datetime' not in df.columns:
        return
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()
    
    ohlc = df.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'amount': 'sum',
        'open_interest': 'last'
    })
    ohlc = ohlc.dropna()
    ohlc = ohlc.reset_index()
    ohlc['code'] = code
    ohlc.to_csv(f'futures_weekly/{code}.csv', index=False)

def main():
    tq.initialize(__file__)
    print("初始化成功")
    
    futures = tq.get_stock_list('92', list_type=1)
    print(f"主力合约: {len(futures)} 个")
    
    contracts = [f['Code'].split('.')[0][:-4] + 'L8.' + f['Code'].split('.')[1] for f in futures]
    print(f"处理: {len(contracts)} 合约")
    
    updated = 0
    for i, code in enumerate(contracts):
        print(f"[{i+1}/{len(contracts)}] {code}", end=" ", flush=True)
        
        latest = get_latest_date(code)
        if latest is None:
            print("无历史数据, 跳过")
            continue
        
        today = datetime.now().strftime('%Y%m%d')
        if latest[:8] >= today:
            print("已是最新")
            continue
        
        result = update_1min(code, latest[:8], today)
        if result is not None and len(result) > 0:
            print(f"+{len(result)}条", end=" ", flush=True)
            updated += 1
            regenerate_periods(code)
            regenerate_weekly(code)
            print("OK")
        else:
            print("无新数据")
        
        time.sleep(0.3)
    
    tq.close()
    print(f"\n完成! 更新了 {updated} 个合约")

if __name__ == '__main__':
    main()