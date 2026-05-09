import os
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QLIB_CSV_DIR = os.path.join(BASE_DIR, 'qlib_csv')

EXCHANGE_MAP = {
    'CFFEX': 'SH',
    'CZCE': 'ZZ',
    'DCE': 'DL',
    'SHFE': 'SH',
    'INE': 'SH',
    'GFE': 'GJ',
}

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

def convert_futures_to_qlib_csv(source_dir, target_dir, period='1min'):
    os.makedirs(target_dir, exist_ok=True)
    
    files = [f for f in os.listdir(source_dir) if f.endswith('.csv')]
    print(f"转换 {len(files)} 个{period}文件...")
    
    for i, fname in enumerate(files):
        code = fname.replace('.csv', '')
        qlib_symbol = convert_code_to_qlib(code)
        
        df = pd.read_csv(os.path.join(source_dir, fname))
        
        if 'datetime' not in df.columns:
            print(f"  [{i+1}/{len(files)}] {code} - 无datetime列")
            continue
        
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
        
        out_name = f"{qlib_symbol}.csv"
        qlib_df.to_csv(os.path.join(target_dir, out_name), index=False)
        print(f"  [{i+1}/{len(files)}] {code} -> {out_name}")
    
    print(f"完成! 文件保存在 {target_dir}")

def convert_all_periods():
    periods = {
        'futures_data': ('qlib_csv_1min', '1min'),
        'futures_5m': ('qlib_csv_5min', '5min'),
        'futures_daily': ('qlib_csv_daily', 'daily'),
    }
    
    for source_dir, (target_name, period) in periods.items():
        source_path = os.path.join(BASE_DIR, source_dir)
        if os.path.exists(source_path):
            target_path = os.path.join(BASE_DIR, target_name)
            convert_futures_to_qlib_csv(source_path, target_path, period)

if __name__ == '__main__':
    convert_all_periods()
    print("\n所有数据转换完成!")
    print("\n转换为 qlib bin 格式:")
    print("  python /mnt/d/data_1m/venv/bin/python scripts/dump_bin.py dump_all \\")
    print("    --data_path qlib_csv_daily \\")
    print("    --qlib_dir qlib_data \\")
    print("    --include_fields open,close,high,low,volume,money,factor \\")
    print("    --date_field_name date \\")
    print("    --symbol_field_name symbol \\")
    print("    --file_suffix .csv")