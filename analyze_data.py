#!/usr/bin/env python3
"""
分析CYC/USDT数据，找出最优RSI参数
"""

import pandas as pd
import numpy as np
import talib.abstract as ta
from datetime import datetime

def analyze_cyc_data():
    # 读取CYC数据
    try:
        df = pd.read_feather('user_data/data/binance/CYC_USDT-5m.feather')
        print(f"数据加载成功，共{len(df)}条记录")
        print(f"时间范围: {df['date'].min()} 到 {df['date'].max()}")
        
        # 计算不同周期的RSI
        df['rsi_14'] = ta.RSI(df, timeperiod=14)
        df['rsi_21'] = ta.RSI(df, timeperiod=21)
        df['rsi_7'] = ta.RSI(df, timeperiod=7)
        
        # 计算价格变化
        df['price_change_5m'] = df['close'].pct_change(1) * 100
        df['price_change_15m'] = df['close'].pct_change(3) * 100
        df['price_change_1h'] = df['close'].pct_change(12) * 100
        df['price_change_4h'] = df['close'].pct_change(48) * 100
        
        # 简化分析：只测试几个关键参数组合
        results = []
        
        # 快速测试几个有希望的组合
        test_params = [
            (14, 30, 70),  # 经典RSI参数
            (14, 35, 65),  # 稍微宽松
            (7, 25, 75),   # 短周期敏感
            (21, 40, 60),  # 长周期稳健
            (14, 25, 80),  # 极端超买超卖
        ]
        
        for rsi_period, buy_threshold, sell_threshold in test_params:
            print(f"测试参数: RSI{rsi_period}, 买入<{buy_threshold}, 卖出>{sell_threshold}")
            
            rsi_col = f'rsi_{rsi_period}'
            
            # 简单回测逻辑
            position = None
            trades = []
            
            for i, row in df.iterrows():
                if pd.isna(row[rsi_col]):
                    continue
                    
                current_price = row['close']
                current_rsi = row[rsi_col]
                
                # 如果没有持仓，检查买入信号
                if position is None:
                    if current_rsi < buy_threshold:
                        position = {
                            'buy_price': current_price,
                            'buy_time': row['date'],
                            'buy_index': i
                        }
                
                # 如果有持仓，检查卖出信号
                elif position is not None:
                    price_change = (current_price - position['buy_price']) / position['buy_price'] * 100
                    
                    # 止损 -2%
                    if price_change <= -2:
                        trades.append({
                            'profit_pct': price_change,
                            'duration_minutes': (row['date'] - position['buy_time']).total_seconds() / 60,
                            'exit_reason': 'stop_loss'
                        })
                        position = None
                    
                    # 目标盈利 +6%
                    elif price_change >= 6:
                        trades.append({
                            'profit_pct': price_change,
                            'duration_minutes': (row['date'] - position['buy_time']).total_seconds() / 60,
                            'exit_reason': 'roi'
                        })
                        position = None
                    
                    # RSI卖出信号
                    elif current_rsi > sell_threshold:
                        trades.append({
                            'profit_pct': price_change,
                            'duration_minutes': (row['date'] - position['buy_time']).total_seconds() / 60,
                            'exit_reason': 'signal'
                        })
                        position = None
            
            if len(trades) > 0:
                trades_df = pd.DataFrame(trades)
                
                total_profit = trades_df['profit_pct'].sum()
                win_rate = len(trades_df[trades_df['profit_pct'] > 0]) / len(trades_df) * 100
                avg_profit = trades_df['profit_pct'].mean()
                
                results.append({
                    'rsi_period': rsi_period,
                    'buy_threshold': buy_threshold,
                    'sell_threshold': sell_threshold,
                    'total_trades': len(trades),
                    'total_profit': total_profit,
                    'win_rate': win_rate,
                    'avg_profit': avg_profit,
                    'avg_duration': trades_df['duration_minutes'].mean()
                })
                
                print(f"  交易次数: {len(trades)}, 总盈利: {total_profit:.2f}%, 胜率: {win_rate:.1f}%")
            else:
                print(f"  无交易")
        
        # 转换为DataFrame并排序
        results_df = pd.DataFrame(results)
        
        if len(results_df) > 0:
            # 按总盈利排序
            best_by_profit = results_df.sort_values('total_profit', ascending=False).head(10)
            print("\n=== 按总盈利排序的前10个参数组合 ===")
            print(best_by_profit.to_string(index=False))
            
            # 按胜率排序（最少10次交易）
            frequent_trades = results_df[results_df['total_trades'] >= 10]
            if len(frequent_trades) > 0:
                best_by_winrate = frequent_trades.sort_values('win_rate', ascending=False).head(10)
                print("\n=== 按胜率排序的前10个参数组合（最少10次交易）===")
                print(best_by_winrate.to_string(index=False))
            
            # 找到最佳参数
            if len(best_by_profit) > 0:
                best_params = best_by_profit.iloc[0]
                print(f"\n=== 最佳参数组合 ===")
                print(f"RSI周期: {best_params['rsi_period']}")
                print(f"买入阈值: {best_params['buy_threshold']}")
                print(f"卖出阈值: {best_params['sell_threshold']}")
                print(f"总交易次数: {best_params['total_trades']}")
                print(f"总盈利: {best_params['total_profit']:.2f}%")
                print(f"胜率: {best_params['win_rate']:.1f}%")
                print(f"平均盈利: {best_params['avg_profit']:.2f}%")
                print(f"平均持仓时长: {best_params['avg_duration']:.0f}分钟")
                
                return best_params
        else:
            print("没有找到符合条件的交易")
            return None
            
    except Exception as e:
        print(f"分析失败: {e}")
        return None

if __name__ == '__main__':
    analyze_cyc_data()