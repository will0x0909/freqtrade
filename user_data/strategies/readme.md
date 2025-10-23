# Freqtrade 策略总结文档

## 项目概述
本文档总结了 freqtrade-strategies 项目中的所有交易策略，包括文件名、策略名称、使用的技术指标、时间框架等关键信息。

## 主策略目录 (`user_data/strategies/`)

### 1. AwesomeMacd.py
- **策略类名**: AwesomeMacd
- **时间框架**: 5m
- **技术指标**: MACD, Awesome Oscillator
- **策略逻辑**: MACD 与 AO 确认

### 2. Bandtastic.py
- **策略类名**: Bandtastic
- **时间框架**: 15m
- **技术指标**: RSI, MFI, 多层布林带 (1,2,3,4 标准差), EMA (动态范围)
- **主要参数**: 买入/卖出 RSI, MFI, EMA 阈值，支持超参数优化
- **策略逻辑**: 
  - **买入**: 价格低于选定布林带下轨，可选 RSI/MFI/EMA 过滤
  - **卖出**: 价格高于选定布林带上轨，可选 RSI/MFI/EMA 过滤
- **特色功能**: 广泛的超参数优化参数，跟踪止损，多层布林带

### 3. BinHV27.py
- **策略类名**: BinHV27
- **时间框架**: 5m
- **技术指标**: 布林带, RSI, MACD
- **策略逻辑**: 布林带突破与 RSI 过滤

### 4. CofiBitStrategy.py
- **策略类名**: CofiBitStrategy
- **时间框架**: 5m
- **技术指标**: Stochastic, EMA, ADX
- **策略逻辑**: Stochastic 与趋势确认

### 5. MACDStrategy.py
- **策略类名**: MACDStrategy
- **时间框架**: 5m
- **技术指标**: MACD, CCI
- **策略逻辑**: MACD 交叉与 CCI 确认（支持超参数优化）

### 6. MACDStrategy_crossed.py
- **策略类名**: MACDStrategy_crossed
- **时间框架**: 5m
- **技术指标**: MACD
- **策略逻辑**: MACD 交叉策略变体

### 7. Strategy004.py
- **策略类名**: Strategy004
- **时间框架**: 1h
- **技术指标**: SMA (20), EMA (20), RSI, MACD, 布林带
- **策略逻辑**: 布林带突破与 RSI 和 MACD 确认
- **特色功能**: 突破策略

### 8. UniversalMACD.py
- **策略类名**: UniversalMACD
- **时间框架**: 5m
- **技术指标**: EMA (12, 26), 通用 MACD 计算
- **策略逻辑**: 
  - **买入/卖出**: 通用 MACD 值在指定范围内
- **特色功能**: 使用比率计算的自定义 MACD 实现