import os
import json
import pandas as pd
from datetime import datetime
import config


class Storage:
    def __init__(self):
        self.data_dir = config.DATA_DIR
        self.cache_dir = config.CACHE_DIR
        self._ensure_dirs()

    def _ensure_dirs(self):
        os.makedirs(config.DATA_1M_DIR, exist_ok=True)
        os.makedirs(config.DATA_DAILY_DIR, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_data_path(self, exchange, period='1m'):
        if period == '1m':
            return os.path.join(config.DATA_1M_DIR, f"{exchange}.parquet")
        else:
            return os.path.join(config.DATA_DAILY_DIR, f"{exchange}.parquet")

    def save_kline_data(self, all_data, period='1m'):
        for exchange, data in all_data.items():
            if not data:
                continue

            records = []
            for code, klines in data.items():
                for kline in klines:
                    record = kline.copy()
                    record['code'] = code
                    records.append(record)

            if not records:
                continue

            df = pd.DataFrame(records)

            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'], format='mixed')

            df = df.sort_values(['code', 'datetime'])

            file_path = self.get_data_path(exchange, period)
            if os.path.exists(file_path):
                existing = pd.read_parquet(file_path)
                df = pd.concat([existing, df]).drop_duplicates(subset=['code', 'datetime'], keep='last')
                df = df.sort_values(['code', 'datetime'])

            csv_path = file_path.replace('.parquet', '.csv')
            df.to_csv(csv_path, index=False)
            print(f"  保存 {exchange}: {len(df)} 条 -> {csv_path}")
            print(f"  保存 {exchange}: {len(df)} 条 -> {file_path}")

        self._update_metadata(all_data, period)

    def _update_metadata(self, all_data, period):
        metadata = self._load_metadata()

        for exchange, data in all_data.items():
            if exchange not in metadata['contracts']:
                metadata['contracts'][exchange] = {}

            for code in data.keys():
                metadata['contracts'][exchange][code] = {
                    'last_update': datetime.now().strftime('%Y-%m-%d'),
                    'record_count': len(data[code])
                }

        metadata['last_update'] = datetime.now().strftime('%Y-%m-%d')
        metadata['version'] = '1.0'

        with open(config.METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _load_metadata(self):
        if os.path.exists(config.METADATA_FILE):
            with open(config.METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'version': '1.0',
            'last_update': '',
            'contracts': {}
        }

    def load_kline_data(self, exchanges=None, codes=None, start_date=None, end_date=None, period='1m'):
        all_dfs = []

        data_dir = config.DATA_1M_DIR if period == '1m' else config.DATA_DAILY_DIR

        files = os.listdir(data_dir) if os.path.exists(data_dir) else []

        for f in files:
            if not f.endswith('.parquet'):
                continue

            exchange = f.replace('.parquet', '')
            if exchanges and exchange not in exchanges:
                continue

            file_path = os.path.join(data_dir, f)
            df = pd.read_parquet(file_path)

            if codes:
                df = df[df['code'].isin(codes)]

            if start_date:
                df = df[df['datetime'] >= pd.to_datetime(start_date)]

            if end_date:
                df = df[df['datetime'] <= pd.to_datetime(end_date)]

            if len(df) > 0:
                all_dfs.append(df)

        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        return pd.DataFrame()

    def get_exchange_stats(self, period='1m'):
        stats = {}
        data_dir = config.DATA_1M_DIR if period == '1m' else config.DATA_DAILY_DIR

        if not os.path.exists(data_dir):
            return stats

        for f in os.listdir(data_dir):
            if f.endswith('.parquet'):
                exchange = f.replace('.parquet', '')
                df = pd.read_parquet(os.path.join(data_dir, f))
                stats[exchange] = {
                    'records': len(df),
                    'codes': df['code'].nunique() if 'code' in df.columns else 0,
                    'date_range': f"{df['datetime'].min()} ~ {df['datetime'].max()}" if 'datetime' in df.columns and len(df) > 0 else 'N/A'
                }

        return stats


if __name__ == '__main__':
    storage = Storage()
    stats = storage.get_exchange_stats()
    print("数据统计:")
    for exchange, s in stats.items():
        print(f"  {exchange}: {s['records']} 条, {s['codes']} 个合约")