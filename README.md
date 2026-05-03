# TDX Futures Data Collection System

Chinese futures K-line data collection system based on TongDaXin (TDX) quantitative interface.

## Features

- Collect 1-minute K-line data for 85+ Chinese futures main contracts
- Support multiple time periods: 1min, 5min, 10min, 15min, 30min, 60min, 120min, daily, weekly
- Incremental update with automatic period regeneration
- Unified Python API for data access

## Data Coverage

| Exchange | Contracts |
|----------|-----------|
| CFFEX (中金所) | IF, IH, IC, IM, TS, TF, T, TL |
| DCE (大商所) | A, B, C, M, Y, P, J, JM, L, V, I, etc. |
| CZCE (郑商所) | SR, CF, ZC, FG, TA, MA, etc. |
| SHFE (上期所) | AU, AG, CU, AL,ZN, PB, etc. |
| INE (能源中心) | SC, LU, NR, EV, BC |
| GFEX (广期所) | SI, LC, PD, PS, PT |

## Requirements

- Python 3.8+
- TongDaXin (通达信) client installed
- TDX quantitative interface (TDX量化接口)

## Installation

```bash
git clone https://github.com/your-repo/tdx-futures-data.git
cd tdx-futures-data

# Ensure TDX is installed and configured
# The default TDX path is D:/new_tdxqh/PYPlugins/user
```

## Quick Start

### 1. Fetch All Data

```bash
# Fetch 1-minute data for all contracts
python fetch_all.py

# Fetch 5-minute data
python fetch_5m.py

# Fetch daily data
python fetch_daily.py
```

### 2. Generate Derived Periods

```bash
# Generate 10/15/30/60/120 minute from 5-minute data
python gen_periods.py

# Generate weekly from daily data
python gen_weekly.py
```

### 3. Incremental Update

```bash
# Update with automatic period regeneration
python incremental_update.py
```

### 4. Use API

```python
from api import get_kline, get_codes

# Get all contracts
codes = get_codes('daily')
print(f"Total contracts: {len(codes)}")

# Get daily K-line
df = get_kline('IFL8.CFF', 'daily')
print(df.head())

# Get 5-minute K-line
df = get_kline('IFL8.CFF', '5min')

# Get any custom period (e.g., 7 minutes)
df = get_kline('IFL8.CFF', minute=7)

# Clear cache
from api import FuturesAPI
FuturesAPI.clear_cache()
```

## API Reference

### `get_kline(code, period='daily', minute=None)`

| Parameter | Type | Description |
|-----------|------|-------------|
| code | str | Contract code, e.g., 'IFL8.CFF' |
| period | str | Pre-computed period: '1min', '5min', '10min', '15min', '30min', '60min', '120min', 'daily', 'weekly' |
| minute | int | Custom minute period for real-time synthesis (optional) |

Returns: `pandas.DataFrame` with columns: datetime, open, high, low, close, volume, amount, open_interest, code

### `get_codes(period='daily')`

Get all contract codes for the specified period.

## Data Structure

```
tdx_futures_data/
├── api.py                 # Unified API
├── config.py              # Configuration
├── fetch_all.py           # Fetch 1min data
├── fetch_5m.py            # Fetch 5min data
├── fetch_daily.py         # Fetch daily data
├── incremental_update.py  # Incremental update
├── gen_periods.py         # Generate derived periods
├── gen_weekly.py          # Generate weekly data
├── futures_data/          # 1min data (~189MB)
├── futures_5m/            # 5min data (~38MB)
├── futures_10m/           # 10min data (~20MB)
├── futures_15m/           # 15min data (~14MB)
├── futures_30m/           # 30min data (~8MB)
├── futures_60m/           # 60min data (~5MB)
├── futures_120m/          # 120min data (~3MB)
├── futures_daily/         # Daily data (~11MB)
└── futures_weekly/        # Weekly data (~2MB)
```

## Configuration

Edit `config.py` to customize:

- TDX plugin path
- Data time range
- Contract list
- Batch size

## License

MIT License

## Contributing

Issues and pull requests are welcome!