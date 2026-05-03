"""
TdxQuant 期货数据系统配置
"""

import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_DIR = os.path.join(BASE_DIR, 'cache')

# 数据目录
DATA_1M_DIR = os.path.join(DATA_DIR, '1m')
DATA_DAILY_DIR = os.path.join(DATA_DIR, 'daily')

# 元数据文件
METADATA_FILE = os.path.join(CACHE_DIR, 'metadata.json')

# TDX接口路径
TDX_PLUGIN_PATH = 'D:/new_tdxqh/PYPlugins/user'

# 数据时间范围
DATA_START_DATE = '2025-07-07'

# 采集配置
MAX_RECORDS_PER_BATCH = 24000  # TDX单次最大支持数量
BATCH_SIZE = 8  # 每批并行获取的合约数
BATCH_DELAY = 2  # 批次间延迟(秒)

# 数据字段
KLINE_FIELDS_1M = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest']
KLINE_FIELDS_DAILY = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'open_interest', 'settle', 'change']

# 期货交易所配置
EXCHANGES = {
    'CFFEX': {'code': 'CFFEX', 'name': '中金所', 'suffix': '.CFF'},
    'DCE': {'code': 'DCE', 'name': '大商所', 'suffix': '.DCE'},
    'CZCE': {'code': 'CZCE', 'name': '郑商所', 'suffix': '.CZC'},
    'SHFE': {'code': 'SHFE', 'name': '上期所', 'suffix': '.SHF'},
    'INE': {'code': 'INE', 'name': '能源中心', 'suffix': '.INE'},
    'GFEX': {'code': 'GFEX', 'name': '广期所', 'suffix': '.GFE'},
}

# 期货品种列表 (主力合约后缀: L8)
FUTURES_CODES = {
    'CFFEX': ['IF', 'IH', 'IC', 'IM', 'TS', 'TF', 'T', 'TL'],
    'DCE': ['A', 'B', 'C', 'M', 'Y', 'P', 'J', 'JM', 'L', 'V', 'I', 'SM', 'RM', 'RS', 'FB', 'SB', 'EB', 'PG', 'PP', 'EG', 'BB', 'BZ', 'CS', 'JD', 'LH', 'RR', 'LG'],
    'CZCE': ['SR', 'CF', 'ZC', 'FG', 'TA', 'MA', 'PF', 'RU', 'WH', 'AP', 'JR', 'CS', 'SM', 'RM', 'OI', 'CY', 'UR', 'SA', 'NR', 'JS', 'RI', 'CJ', 'PK', 'PR', 'PX', 'SF', 'SH'],
    'SHFE': ['AU', 'AG', 'CU', 'AL', 'ZN', 'PB', 'RU', 'FU', 'RB', 'HC', 'WR', 'BU', 'NI', 'SN', 'AD', 'AO', 'BC', 'BR', 'EC', 'LU', 'NR', 'OP', 'SP', 'SS'],
    'INE': ['SC', 'LU', 'NR', 'EV', 'BC'],
    'GFEX': ['SI', 'LC', 'PD', 'PS', 'PT'],
}