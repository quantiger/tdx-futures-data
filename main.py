import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from src.api import get_api


def main():
    print(f"开始采集期货1分钟K线数据")
    print(f"时间范围: {config.DATA_START_DATE} ~ {datetime.now().strftime('%Y-%m-%d')}")
    print(f"交易所: {list(config.EXCHANGES.keys())}")

    total_codes = sum(len(codes) for codes in config.FUTURES_CODES.values())
    print(f"合约数量: {total_codes}")

    api = get_api()

    start_time = time.time()

    try:
        result = api.fetch_and_save(
            start_date=config.DATA_START_DATE,
            end_date=datetime.now().strftime('%Y-%m-%d'),
            period='1m'
        )

        elapsed = time.time() - start_time
        print(f"\n采集完成! 耗时: {elapsed:.1f}秒")

        print("\n最终数据统计:")
        stats = api.get_stats('1m')
        total_records = 0
        for exchange, s in stats.items():
            print(f"  {exchange}: {s['records']} 条, {s['codes']} 个合约, {s['date_range']}")
            total_records += s['records']
        print(f"\n总计: {total_records} 条")

    except Exception as e:
        print(f"采集失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        api.close()


if __name__ == '__main__':
    main()