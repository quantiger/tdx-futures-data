import os
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.api import FuturesDataAPI


class IncrementalUpdater:
    def __init__(self, api=None):
        self.api = api or FuturesDataAPI()

    def get_last_update_date(self):
        metadata_file = config.METADATA_FILE
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                return metadata.get('last_update', '')
        return None

    def update_since(self, since_date=None):
        if since_date is None:
            since_date = self.get_last_update_date()

        if since_date is None:
            print("首次全量更新...")
            return self.api.fetch_and_save()

        print(f"增量更新 from {since_date}...")

        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        if since_date == today:
            print("数据已是最新")
            return {}

        return self.api.fetch_and_save(start_date=since_date, end_date=today)

    def update_last_n_days(self, days=1):
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        print(f"更新最近 {days} 天: {start_date} ~ {end_date}")
        return self.api.fetch_and_save(start_date=start_date, end_date=end_date)


if __name__ == '__main__':
    updater = IncrementalUpdater()
    last_date = updater.get_last_update_date()
    print(f"上次更新: {last_date}")

    updater.update_last_n_days(1)

    print("\n更新后统计:")
    stats = updater.api.get_stats('1m')
    for ex, s in stats.items():
        print(f"  {ex}: {s}")

    updater.api.close()