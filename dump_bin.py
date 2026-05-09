import os
import pandas as pd
import numpy as np
from pathlib import Path

QLIB_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qlib_data')

class QlibBinConverter:
    def __init__(self, qlib_dir):
        self.qlib_dir = Path(qlib_dir)
        self.qlib_dir.mkdir(parents=True, exist_ok=True)
        
    def dump_all(self, csv_dir, include_fields, date_field='date', symbol_field='symbol', freq='day'):
        csv_path = Path(csv_dir)
        if not csv_path.exists():
            raise ValueError(f"CSV path does not exist: {csv_path}")
        
        fields = [f.strip() for f in include_fields.split(',')]
        print(f"转换字段: {fields}")
        
        all_data = []
        csv_files = list(csv_path.glob('*.csv'))
        print(f"找到 {len(csv_files)} 个CSV文件")
        
        for f in csv_files:
            df = pd.read_csv(f)
            if date_field in df.columns and symbol_field in df.columns:
                all_data.append(df)
        
        if not all_data:
            print("未找到有效数据")
            return
        
        combined = pd.concat(all_data, ignore_index=True)
        combined[date_field] = pd.to_datetime(combined[date_field])
        
        instruments = combined[symbol_field].unique()
        print(f"合约数: {len(instruments)}")
        
        calendars = combined[date_field].dt.strftime('%Y-%m-%d').unique()
        calendars = sorted(calendars)
        print(f"交易日历: {calendars[0]} ~ {calendars[-1]}")
        
        cal_dir = self.qlib_dir / 'calendars'
        cal_dir.mkdir(exist_ok=True)
        with open(cal_dir / 'day.txt', 'w') as f:
            for cal in calendars:
                f.write(cal + '\n')
        
        inst_dir = self.qlib_dir / 'instruments'
        inst_dir.mkdir(exist_ok=True)
        with open(inst_dir / 'all.txt', 'w') as f:
            for inst in instruments:
                f.write(inst + '\n')
        
        for field in fields:
            if field not in combined.columns:
                print(f"跳过无效字段: {field}")
                continue
            
            field_dir = self.qlib_dir / 'features' / field
            field_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"处理字段: {field}")
            
            for inst in instruments:
                inst_data = combined[combined[symbol_field] == inst].copy()
                inst_data = inst_data.set_index(date_field)
                inst_data = inst_data.sort_index()
                
                if freq == 'day':
                    out_file = field_dir / f'{inst}.bin'
                else:
                    freq_dir = field_dir / freq
                    freq_dir.mkdir(exist_ok=True)
                    out_file = freq_dir / f'{inst}.bin'
                
                values = inst_data[field].values.astype(np.float64)
                values.tofile(out_file)
            
            print(f"  {field} 完成")
        
        print(f"\n完成! 数据保存在: {self.qlib_dir}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', required=True)
    parser.add_argument('--qlib_dir', required=True)
    parser.add_argument('--include_fields', default='open,close,high,low,volume,money,factor')
    parser.add_argument('--date_field_name', default='date')
    parser.add_argument('--symbol_field_name', default='symbol')
    parser.add_argument('--freq', default='day')
    args = parser.parse_args()
    
    converter = QlibBinConverter(args.qlib_dir)
    converter.dump_all(
        args.data_path,
        args.include_fields,
        args.date_field_name,
        args.symbol_field_name,
        args.freq
    )

if __name__ == '__main__':
    main()