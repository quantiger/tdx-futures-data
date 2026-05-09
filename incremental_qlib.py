import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq
import pandas as pd
import time
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCHANGE_MAP = {
    'CFFEX': 'SH',
    'CZCE': 'ZZ',
    'DCE': 'DL',
    'SHFE': 'SH',
    'INE': 'SH',
    'GFE': 'GJ',
}

QLIB_1MIN_DIR = os.path.join(BASE_DIR, 'qlib_csv_1min')
QLIB_5MIN_DIR = os.path.join(BASE_DIR, 'qlib_csv_5min')
QLIB_DAILY_DIR = os.path.join(BASE_DIR, 'qlib_csv_daily')

def convert_code_to_qlib(code):
    parts = code.rsplit('.', 1)
    if len(parts) != 2:
        return code
    symbol, exchange = parts[0], parts[1]
    prefix = symbol[:-1]
    month = symbol[-1]
    month_map = {'1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06',
                 '7': '07', '8': '08', '9': '09', '0': '10', 'F': '01', 'G': '02',
                 'H': '03', 'J': '04', 'K': '05', 'M': '06', 'N': '07', 'Q': '08',
                 'U': '09', 'V': '10', 'X': '11', 'Z': '12'}
    month_num = month_map.get(month, '08')
    exchange_code = EXCHANGE_MAP.get(exchange, exchange)
    return f"{prefix}{month_num}.{exchange_code}"

def save_qlib_csv(code, df, period_dir):
    qlib_symbol = convert_code_to_qlib(code)
    os.makedirs(period_dir, exist_ok=True)
    out_path = os.path.join(period_dir, f"{qlib_symbol}.csv")
    
    qlib_df = pd.DataFrame({
        'symbol': qlib_symbol,
        'date': pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S'),
        'open': df['open'],
        'close': df['close'],
        'high': df['high'],
        'low': df['low'],
        'volume': df['volume'],
        'money': df.get('amount', df.get('volume', 0)),
        'factor': 1.0,
    })
    
    if os.path.exists(out_path):
        existing = pd.read_csv(out_path)
        combined = pd.concat([existing, qlib_df]).drop_duplicates(subset=['date'])
        combined = combined.sort_values('date').reset_index(drop=True)
        combined.to_csv(out_path, index=False)
    else:
        qlib_df.to_csv(out_path, index=False)

def fetch_1min(code, start_date, end_date):
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
    return merged

def fetch_5min(code, start_date, end_date):
    field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
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
    return merged

def fetch_daily(code, start_date, end_date):
    field_list = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'VolInStock']
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
    return merged

def get_latest_date_qlib(code, period_dir):
    qlib_symbol = convert_code_to_qlib(code)
    path = os.path.join(period_dir, f"{qlib_symbol}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    if 'date' not in df.columns:
        return None
    return df['date'].max()

def update_1min_all():
    contracts_dir = os.path.join(BASE_DIR, 'futures_data')
    if not os.path.exists(contracts_dir):
        print("futures_data 目录不存在")
        return
    contracts = [f.replace('.csv', '') for f in os.listdir(contracts_dir) if f.endswith('.csv')]
    print(f"共 {len(contracts)} 个合约")
    print(f"输出目录: {QLIB_1MIN_DIR}")
    
    updated = 0
    for i, code in enumerate(contracts):
        print(f"[{i+1}/{len(contracts)}] {code}", end=" ", flush=True)
        
        latest = get_latest_date_qlib(code, QLIB_1MIN_DIR)
        today = datetime.now().strftime('%Y%m%d')
        
        if latest is not None and latest[:8] >= today:
            print("已是最新")
            continue
        
        start = latest[:8] if latest else '20250701'
        result = fetch_1min(code, start, today)
        
        if result is not None and len(result) > 0:
            save_qlib_csv(code, result, QLIB_1MIN_DIR)
            print(f"+{len(result)}条 OK")
            updated += 1
        else:
            print("无新数据")
        
        time.sleep(0.3)
    
    print(f"\n1min完成! 更新了 {updated} 个合约")

def update_5min_all():
    contracts_dir = os.path.join(BASE_DIR, 'futures_data')
    if not os.path.exists(contracts_dir):
        print("futures_data 目录不存在")
        return
    contracts = [f.replace('.csv', '') for f in os.listdir(contracts_dir) if f.endswith('.csv')]
    print(f"共 {len(contracts)} 个合约")
    print(f"输出目录: {QLIB_5MIN_DIR}")
    
    updated = 0
    for i, code in enumerate(contracts):
        print(f"[{i+1}/{len(contracts)}] {code}", end=" ", flush=True)
        
        latest = get_latest_date_qlib(code, QLIB_5MIN_DIR)
        today = datetime.now().strftime('%Y%m%d')
        
        if latest is not None and latest[:8] >= today:
            print("已是最新")
            continue
        
        start = latest[:8] if latest else '20250701'
        result = fetch_5min(code, start, today)
        
        if result is not None and len(result) > 0:
            save_qlib_csv(code, result, QLIB_5MIN_DIR)
            print(f"+{len(result)}条 OK")
            updated += 1
        else:
            print("无新数据")
        
        time.sleep(0.3)
    
    print(f"\n5min完成! 更新了 {updated} 个合约")

def update_daily_all():
    contracts_dir = os.path.join(BASE_DIR, 'futures_data')
    if not os.path.exists(contracts_dir):
        print("futures_data 目录不存在")
        return
    contracts = [f.replace('.csv', '') for f in os.listdir(contracts_dir) if f.endswith('.csv')]
    print(f"共 {len(contracts)} 个合约")
    print(f"输出目录: {QLIB_DAILY_DIR}")
    
    updated = 0
    for i, code in enumerate(contracts):
        print(f"[{i+1}/{len(contracts)}] {code}", end=" ", flush=True)
        
        latest = get_latest_date_qlib(code, QLIB_DAILY_DIR)
        today = datetime.now().strftime('%Y%m%d')
        
        if latest is not None and latest[:8] >= today:
            print("已是最新")
            continue
        
        start = latest[:8] if latest else '20150101'
        result = fetch_daily(code, start, today)
        
        if result is not None and len(result) > 0:
            save_qlib_csv(code, result, QLIB_DAILY_DIR)
            print(f"+{len(result)}条 OK")
            updated += 1
        else:
            print("无新数据")
        
        time.sleep(0.3)
    
    print(f"\ndaily完成! 更新了 {updated} 个合约")

def main():
    tq.initialize(__file__)
    print("初始化成功")
    print("采集 1min 数据...")
    update_1min_all()
    print("\n采集 5min 数据...")
    update_5min_all()
    print("\n采集 daily 数据...")
    update_daily_all()
    tq.close()
    print("\n全部完成!")
    print(f"\n转换为 qlib bin 格式:")
    print(f"  cd {BASE_DIR}")
    print(f"  /mnt/d/data_1m/venv/bin/python -m qlib.workflow.cli dump_all \\")
    print(f"    --data_path qlib_csv_daily \\")
    print(f"    --qlib_dir qlib_data \\")
    print(f"    --include_fields open,close,high,low,volume,money,factor \\")
    print(f"    --date_field_name date \\")
    print(f"    --symbol_field_name symbol \\")
    print(f"    --file_suffix .csv")

if __name__ == '__main__':
    main()