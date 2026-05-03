import sys
sys.path.insert(0, 'D:/new_tdxqh/PYPlugins/user')
from tqcenter import tq

tq.initialize(__file__)

# 获取期货列表 92=国内期货主力合约
futures = tq.get_stock_list('92', list_type=1)
print(f"主力合约数量: {len(futures)}")
print("\n主力合约列表:")
for f in futures:
    print(f)

tq.close()