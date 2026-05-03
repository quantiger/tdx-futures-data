import os
import sys
import pandas as pd
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.fetcher import TdxFetcher
from src.storage import Storage


class FuturesDataAPI:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.dirname(os.path.abspath(__file__))
        self.storage = Storage()
        self.fetcher = None

    def _get_fetcher(self):
        if self.fetcher is None:
            self.fetcher = TdxFetcher()
        return self.fetcher

    def get_kline(self, codes=None, exchanges=None, start_time=None, end_time=None, period='1m'):
        return self.storage.load_kline_data(
            exchanges=exchanges,
            codes=codes,
            start_date=start_time,
            end_date=end_time,
            period=period
        )

    def fetch_and_save(self, exchanges=None, start_date=None, end_date=None, period='1m'):
        fetcher = self._get_fetcher()

        if exchanges is None:
            exchanges = list(config.EXCHANGES.keys())

        if start_date is None:
            start_date = config.DATA_START_DATE.replace('-', '')

        if end_date is None:
            from datetime import datetime
            end_date = datetime.now().strftime('%Y%m%d')

        print("\n刷新期货行情缓存...")
        fetcher.refresh_cache(markets=['QH'])

        print("刷新K线数据(下载盘后数据,可能需要较长时间)...")
        all_contracts = []
        for exchange in exchanges:
            all_contracts.extend(fetcher.get_main_contracts(exchange))
        fetcher.refresh_kline(all_contracts, period=period)

        print("等待数据下载完成(60秒)...")
        time.sleep(60)

        print("再次刷新K线...")
        fetcher.refresh_kline(all_contracts, period=period)

        time.sleep(30)

        all_data = {}

        for exchange in exchanges:
            print(f"\n[{exchange}] 开始获取...")
            contracts = fetcher.get_main_contracts(exchange)
            print(f"  合约数量: {len(contracts)}")

            data = fetcher.get_kline_data(contracts, start_date.replace('-', ''), end_date.replace('-', ''), period)
            all_data[exchange] = data

        print("\n保存数据...")
        self.storage.save_kline_data(all_data, period)

        return all_data

    def incremental_update(self, period='1m'):
        fetcher = self._get_fetcher()

        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y%m%d')

        all_data = {}
        exchanges = list(config.EXCHANGES.keys())

        for exchange in exchanges:
            contracts = fetcher.get_main_contracts(exchange)
            data = fetcher.get_kline_data(contracts, today, today, period)
            all_data[exchange] = data

        self.storage.save_kline_data(all_data, period)
        return all_data

    def get_contracts(self, exchange=None):
        if exchange:
            return config.FUTURES_CODES.get(exchange, [])
        return config.FUTURES_CODES

    def get_exchanges(self):
        return list(config.EXCHANGES.keys())

    def get_stats(self, period='1m'):
        return self.storage.get_exchange_stats(period)

    def close(self):
        if self.fetcher:
            self.fetcher.close()
            self.fetcher = None


def get_api(data_dir=None):
    return FuturesDataAPI(data_dir=data_dir)


if __name__ == '__main__':
    api = get_api()

    print("交易所列表:", api.get_exchanges())

    print("\n数据统计:")
    stats = api.get_stats('1m')
    for ex, s in stats.items():
        print(f"  {ex}: {s}")

    api.close()