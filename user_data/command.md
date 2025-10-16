# COAI 数据回测命令记录

## 1. 获取 COAI 数据

### 获取最近 48 小时的数据
```bash
# 获取最近 48 小时的 COAI 数据（5分钟间隔）
 python3 fetch_alpha_data.py --token-ids 5 2420818 2420842 2420856 2420877 2420893 2420900 2420904 2420915 2420920 2420926 2420944 2420967 2420975 2420977 2420982 2421006 2421029 2421045 2421054 2421094 2421101 2421192 --limit 1500
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

## 8. 重要：修复市场信息依赖问题 (2025-10-16)

### 问题描述
当回测不存在于交易所的 Alpha 代币时，会出现如下错误：
```
ValueError: Can't get market information for symbol PFVS/USDT
```

### 最终解决方案
直接修改 freqtrade 源码中的 `_get_stake_amount_limit` 函数，在找不到市场信息时提供默认值：

#### 1. 定位文件
```bash
# 找到 freqtrade 安装路径
python -c "import freqtrade; print(freqtrade.__file__)"
# 通常在: /opt/anaconda3/envs/freqtrade/lib/python3.11/site-packages/freqtrade/exchange/exchange.py
```

#### 2. 修改文件
编辑 `freqtrade/exchange/exchange.py` 文件，在 `_get_stake_amount_limit` 函数中找到如下代码：

**原代码 (约第1031行):**
```python
        except KeyError:
            raise ValueError(f"Can't get market information for symbol {pair}")
```

**修改为:**
```python
        except KeyError:
            # 回测模式下提供默认值，避免市场信息依赖
            print(f"Warning: No market info for {pair}, using defaults for backtesting")
            if limit == "min":
                return 0.1  # 最小 stake amount 默认值
            else:
                return float("inf")  # 最大 stake amount 默认值
```

#### 3. 验证修复
修改后即可正常回测 Alpha 代币：
```bash
freqtrade backtesting -c user_data/config_alpha.json --strategy AlphaTestStrategy --timeframe 1h -p PFVS/USDT
```

### 其他解决方案（已测试但不够有效）
1. ✗ 配置文件中添加 `"skip_pair_validation": true` - 无效
2. ✗ 使用修复脚本 `fix_alpha_backtesting.py` - 无效
3. ✓ **直接修改源码** - 最终有效解决方案

### 配置要求
确保配置文件中包含：
```json
{
    "exchange": {
        "skip_pair_validation": true
    },
    "pairlists": [
        {
            "method": "StaticPairList",
            "allow_inactive": true
        }
    ]
}
```

---

最后更新: 2025-10-16
状态: 成功解决 Alpha 代币回测问题
