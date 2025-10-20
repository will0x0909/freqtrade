#!/usr/bin/env python3
"""
深度分析CYC市场行为，找出其特殊规律
"""

import pandas as pd
import numpy as np
import talib.abstract as ta

def analyze_market_behavior():
    df = pd.read_feather('user_data/data/binance/CYC_USDT-5m.feather')
    
    # 计算各种技术指标
    df['rsi'] = ta.RSI(df, timeperiod=14)
    df['rsi_7'] = ta.RSI(df, timeperiod=7)
    df['volume_sma'] = ta.SMA(df['volume'], timeperiod=20)
    df['price_sma_20'] = ta.SMA(df['close'], timeperiod=20)
    
    # 计算价格变化
    df['pct_change_1'] = df['close'].pct_change(1) * 100  # 下一个5分钟
    df['pct_change_3'] = df['close'].pct_change(3) * 100  # 下一个15分钟
    df['pct_change_12'] = df['close'].pct_change(12) * 100 # 下一个1小时
    
    print(f"数据加载成功，共{len(df)}条记录")
    print(f"时间范围: {df['date'].min()} 到 {df['date'].max()}")
    print(f"市场总体变化: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
    
    # 分析RSI信号的预测性
    print("\n=== RSI信号的未来价格变化分析 ===")
    
    # RSI极值情况下的后续表现
    oversold = df[df['rsi'] < 30].copy()
    overbought = df[df['rsi'] > 70].copy()
    
    if len(oversold) > 0:
        print(f"RSI<30 (超卖) 信号: {len(oversold)}次")
        print(f"  后续5分钟平均涨幅: {oversold['pct_change_1'].mean():.3f}%")
        print(f"  后续15分钟平均涨幅: {oversold['pct_change_3'].mean():.3f}%") 
        print(f"  后续1小时平均涨幅: {oversold['pct_change_12'].mean():.3f}%")
        print(f"  5分钟上涨概率: {(oversold['pct_change_1'] > 0).mean() * 100:.1f}%")
    
    if len(overbought) > 0:
        print(f"RSI>70 (超买) 信号: {len(overbought)}次")
        print(f"  后续5分钟平均涨幅: {overbought['pct_change_1'].mean():.3f}%")
        print(f"  后续15分钟平均涨幅: {overbought['pct_change_3'].mean():.3f}%")
        print(f"  后续1小时平均涨幅: {overbought['pct_change_12'].mean():.3f}%")
        print(f"  5分钟下跌概率: {(overbought['pct_change_1'] < 0).mean() * 100:.1f}%")
    
    # 分析最佳入场时机
    print("\n=== 寻找最佳入场信号组合 ===")
    
    # 测试多条件组合
    test_conditions = [
        ("RSI<25", "df['rsi'] < 25"),
        ("RSI<20", "df['rsi'] < 20"),
        ("RSI>80", "df['rsi'] > 80"),
        ("RSI>85", "df['rsi'] > 85"),
        ("RSI<25 & 价格<SMA20", "(df['rsi'] < 25) & (df['close'] < df['price_sma_20'])"),
        ("RSI>80 & 价格>SMA20", "(df['rsi'] > 80) & (df['close'] > df['price_sma_20'])"),
        ("RSI<30 & 成交量放大", "(df['rsi'] < 30) & (df['volume'] > df['volume_sma'])"),
        ("RSI>70 & 成交量放大", "(df['rsi'] > 70) & (df['volume'] > df['volume_sma'])"),
    ]
    
    for condition_name, condition_code in test_conditions:
        try:
            signals = df[eval(condition_code)].copy()
            if len(signals) > 10:  # 至少要有10个信号
                print(f"\n{condition_name}: {len(signals)}次信号")
                print(f"  后续5分钟平均涨幅: {signals['pct_change_1'].mean():.3f}%")
                print(f"  后续15分钟平均涨幅: {signals['pct_change_3'].mean():.3f}%")
                print(f"  后续1小时平均涨幅: {signals['pct_change_12'].mean():.3f}%")
                print(f"  5分钟正收益概率: {(signals['pct_change_1'] > 0).mean() * 100:.1f}%")
                print(f"  15分钟正收益概率: {(signals['pct_change_3'] > 0).mean() * 100:.1f}%")
                print(f"  1小时正收益概率: {(signals['pct_change_12'] > 0).mean() * 100:.1f}%")
        except:
            continue
    
    # 寻找反向指标：什么时候不应该交易
    print("\n=== 识别应该避免的交易时机 ===")
    
    # 成交量异常时的表现
    low_volume = df[df['volume'] < df['volume_sma'] * 0.5]
    high_volume = df[df['volume'] > df['volume_sma'] * 2]
    
    if len(low_volume) > 10:
        print(f"低成交量时期 (< 0.5x平均): {len(low_volume)}次")
        print(f"  后续1小时平均涨幅: {low_volume['pct_change_12'].mean():.3f}%")
    
    if len(high_volume) > 10:
        print(f"高成交量时期 (> 2x平均): {len(high_volume)}次")
        print(f"  后续1小时平均涨幅: {high_volume['pct_change_12'].mean():.3f}%")
    
    # 寻找持续趋势
    print("\n=== 趋势分析 ===")
    df['trend_5'] = (df['close'] > df['close'].shift(12)).astype(int)  # 1小时趋势
    
    uptrend = df[df['trend_5'] == 1]
    downtrend = df[df['trend_5'] == 0]
    
    print(f"上升趋势期间RSI<30信号表现:")
    uptrend_oversold = uptrend[uptrend['rsi'] < 30]
    if len(uptrend_oversold) > 5:
        print(f"  信号次数: {len(uptrend_oversold)}")
        print(f"  后续1小时平均涨幅: {uptrend_oversold['pct_change_12'].mean():.3f}%")
    
    print(f"下降趋势期间RSI>70信号表现:")
    downtrend_overbought = downtrend[downtrend['rsi'] > 70]
    if len(downtrend_overbought) > 5:
        print(f"  信号次数: {len(downtrend_overbought)}")
        print(f"  后续1小时平均涨幅: {downtrend_overbought['pct_change_12'].mean():.3f}%")

if __name__ == '__main__':
    analyze_market_behavior()