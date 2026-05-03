"""
Futures K-line Data API
统一期货K线数据接口
"""
import pandas as pd
import os
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PERIOD_DIR = {
    '1min': 'futures_data',
    '5min': 'futures_5m',
    '10min': 'futures_10m',
    '15min': 'futures_15m',
    '30min': 'futures_30m',
    '60min': 'futures_60m',
    '120min': 'futures_120m',
    'daily': 'futures_daily',
    'weekly': 'futures_weekly'
}

class FuturesAPI:
    _cache = {}
    
    @classmethod
    def get_codes(cls, period: str = 'daily') -> list:
        """获取指定周期的所有合约代码"""
        dir_name = PERIOD_DIR.get(period)
        if not dir_name:
            return []
        path = os.path.join(BASE_DIR, dir_name)
        if not os.path.exists(path):
            return []
        return [f.replace('.csv', '') for f in os.listdir(path) if f.endswith('.csv')]
    
    @classmethod
    def load(cls, code: str, period: str = 'daily') -> Optional[pd.DataFrame]:
        """加载指定合约的K线数据"""
        cache_key = f"{code}_{period}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        dir_name = PERIOD_DIR.get(period)
        if not dir_name:
            return None
        
        path = os.path.join(BASE_DIR, dir_name, f"{code}.csv")
        if not os.path.exists(path):
            return None
        
        df = pd.read_csv(path)
        cls._cache[cache_key] = df
        return df
    
    @classmethod
    def load_multi(cls, codes: list, period: str = 'daily') -> dict:
        """批量加载多个合约"""
        return {code: cls.load(code, period) for code in codes}
    
    @classmethod
    def resample(cls, df: pd.DataFrame, minute: int) -> pd.DataFrame:
        """从1分钟数据实时合成任意分钟K线
        
        Args:
            df: 1分钟K线DataFrame
            minute: 目标周期(分钟), 如3, 7, 11等任意值
        
        Returns:
            合成后的K线DataFrame
        """
        if 'datetime' not in df.columns:
            return df
        
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index('datetime').sort_index()
        
        period_str = f'{minute}min'
        ohlc = df.resample(period_str).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum',
            'open_interest': 'last',
            'code': 'last'
        })
        ohlc = ohlc.dropna()
        return ohlc.reset_index()
    
    @classmethod
    def get(cls, code: str, period: str = 'daily', minute: Optional[int] = None) -> Optional[pd.DataFrame]:
        """获取K线数据
        
        Args:
            code: 合约代码, 如 'IFL8.CFF'
            period: 预计算周期 ('1min'/'5min'/'10min'/'15min'/'30min'/'60min'/'120min'/'daily'/'weekly')
            minute: 自定义分钟数, 仅当预计算周期不满足时使用(从1min实时合成)
        
        Returns:
            K线DataFrame
        """
        if minute is not None:
            df_1min = cls.load(code, '1min')
            if df_1min is None:
                return None
            return cls.resample(df_1min, minute)
        
        return cls.load(code, period)
    
    @classmethod
    def clear_cache(cls):
        """清除缓存"""
        cls._cache.clear()

def get_kline(code: str, period: str = 'daily', minute: Optional[int] = None) -> Optional[pd.DataFrame]:
    """便捷函数: 获取K线数据"""
    return FuturesAPI.get(code, period, minute)

def get_codes(period: str = 'daily') -> list:
    """便捷函数: 获取所有合约"""
    return FuturesAPI.get_codes(period)

__all__ = ['FuturesAPI', 'get_kline', 'get_codes']