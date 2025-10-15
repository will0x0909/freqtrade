# COAI 数据回测命令记录

## 1. 获取 COAI 数据

### 获取最近 48 小时的数据
```bash
# 获取最近 48 小时的 COAI 数据（5分钟间隔）
python3 fetch_alpha_data.py --symbol ALPHA_428USDT --interval 5m --recent-hours 48 -o coai_temp.csv
```

### 转换为 Freqtrade 格式
```bash
# 转换为 Freqtrade feather 格式
python3 -c "
import pandas as pd
from datetime import datetime

# 读取 CSV 并转换为 feather 格式
df = pd.read_csv('coai_temp.csv')
df_formatted = pd.DataFrame({
    'date': pd.to_datetime(df['timestamp']).dt.tz_localize('UTC'),
    'open': df['open'],
    'high': df['high'], 
    'low': df['low'],
    'close': df['close'],
    'volume': df['volume']
})

# 保存为 feather 格式
df_formatted.to_feather('user_data/data/binance/COAI_USDT-5m.feather')
print('COAI 数据已转换并保存')
"

# 清理临时文件
rm coai_temp.csv
```

## 2. 启动回测

```bash
# 使用 COAI 数据进行回测
freqtrade backtesting -c user_data/config_alpha.json --strategy AlphaTestStrategy --fee 0.001
```

## 3. 启动 Web UI

```bash
# 启动 Web UI（后台运行）
freqtrade webserver -c user_data/config_alpha.json &

# 访问地址: http://127.0.0.1:8080
# 用户名: freqtrader
# 密码: SuperSecurePassword
```

## 4. 关键配置文件设置

user_data/config_alpha.json 中的重要配置：
```json
{
    "pair_whitelist": ["COAI/USDT"],
    "pairlists": [
        {
            "method": "StaticPairList",
            "allow_inactive": true
        }
    ],
    "skip_pair_validation": true
}
```

## 5. 一键执行脚本

创建 run_coai_backtest.sh：
```bash
#!/bin/bash
echo "开始获取 COAI 数据..."
python3 fetch_alpha_data.py --symbol ALPHA_428USDT --interval 5m --recent-hours 48 -o coai_temp.csv

echo "转换数据格式..."
python3 -c "
import pandas as pd
df = pd.read_csv('coai_temp.csv')
df_formatted = pd.DataFrame({
    'date': pd.to_datetime(df['timestamp']).dt.tz_localize('UTC'),
    'open': df['open'], 'high': df['high'], 'low': df['low'],
    'close': df['close'], 'volume': df['volume']
})
df_formatted.to_feather('user_data/data/binance/COAI_USDT-5m.feather')
print('数据转换完成')
"

rm coai_temp.csv

echo "启动回测..."
freqtrade backtesting -c user_data/config_alpha.json --strategy AlphaTestStrategy --fee 0.001

echo "启动 Web UI..."
freqtrade webserver -c user_data/config_alpha.json
```

执行脚本：
```bash
chmod +x run_coai_backtest.sh
./run_coai_backtest.sh
```

## 6. 其他有用命令

### 查看数据
```bash
# 查看可用数据
freqtrade list-data -c user_data/config_alpha.json
```

### 获取不同时间范围的数据
```bash
# 获取更多小时的数据
python3 fetch_alpha_data.py --symbol ALPHA_428USDT --interval 5m --recent-hours 72 -o coai_temp.csv

# 获取指定时间范围的数据
python3 fetch_alpha_data.py --symbol ALPHA_428USDT --interval 5m --start-time "2025-10-14 00:00:00" --end-time "2025-10-15 23:59:59" -o coai_temp.csv
```

### 使用不同策略
```bash
# 使用自定义策略
freqtrade backtesting -c user_data/config_alpha.json --strategy YourCustomStrategy --fee 0.001
```

### 停止后台进程
```bash
# 查找并停止 freqtrade 进程
ps aux | grep freqtrade
kill <process_id>
```

## 7. 问题解决方案记录

### 关键解决方案
- 交易对兼容性: 配置 "allow_inactive": true 允许非活跃交易对
- 费用计算错误: 使用 --fee 0.001 设置固定费用避免市场查询
- 数据格式: 使用 feather 格式与 Freqtrade 兼容

### 成功配置要点
1. pairlists 中设置 "allow_inactive": true
2. 使用 --fee 参数避免交易所费用查询
3. 数据文件命名格式：COAI_USDT-5m.feather
4. 确保数据列格式：['date', 'open', 'high', 'low', 'close', 'volume']

---

最后更新: 2025-10-15
状态: 成功运行 COAI 回测
