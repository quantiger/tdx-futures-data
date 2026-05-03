import sys
sys.path.insert(0, '/mnt/d/data_1m/tdx_futures_data')
from api import get_kline, get_codes

print("=== 测试预计算周期 ===")
codes = get_codes('daily')
print(f"日线合约数: {len(codes)}")
df = get_kline('IFL8.CFF', 'daily')
print(f"IF日线: {len(df)} 条")

print("\n=== 测试5分钟 ===")
df5 = get_kline('IFL8.CFF', '5min')
print(f"IF5分钟: {len(df5)} 条")

print("\n=== 测试任意分钟(7分钟) ===")
df7 = get_kline('IFL8.CFF', minute=7)
print(f"IF7分钟(实时合成): {len(df7)} 条")

print("\n=== 测试API ===")
df15 = get_kline('AGL8.SHF', '15min')
print(f"AG15分钟: {len(df15)} 条")

df30 = get_kline('AGL8.SHF', '30min')
print(f"AG30分钟: {len(df30)} 条")

df_w = get_kline('AGL8.SHF', 'weekly')
print(f"AG周线: {len(df_w)} 条")

print("\n完成!")