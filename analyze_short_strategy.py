#!/usr/bin/env python3
"""
分析CYC/USDT的做空策略
"""

import pandas as pd
import numpy as np
import talib.abstract as ta

def analyze_short_strategy():
    df = pd.read_feather('user_data/data/binance/CYC_USDT-5m.feather')
    df['rsi'] = ta.RSI(df, timeperiod=14)
    
    print(f"数据加载成功，共{len(df)}条记录")
    print(f"市场总体变化: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")
    
    # 做空策略：RSI高时卖出（做空），RSI低时买回（平仓）
    results = []
    
    # 测试不同的做空参数
    short_params = [
        (70, 30),  # RSI>70做空，RSI<30平仓
        (75, 35),  # 更极端
        (65, 25),  # 更敏感
        (80, 40),  # 更保守
        (75, 30),  # 混合
    ]
    
    for short_threshold, cover_threshold in short_params:
        print(f"\n测试做空策略: RSI>{short_threshold}做空, RSI<{cover_threshold}平仓")
        
        position = None
        trades = []
        
        for i, row in df.iterrows():
            if pd.isna(row['rsi']):
                continue
                
            current_price = row['close']
            current_rsi = row['rsi']
            
            # 做空信号：RSI过高
            if position is None and current_rsi > short_threshold:
                position = {
                    'short_price': current_price,
                    'short_time': row['date'],
                }
            
            # 平仓信号
            elif position is not None:
                # 做空的盈亏计算：(做空价格 - 当前价格) / 做空价格 * 100
                price_change = (position['short_price'] - current_price) / position['short_price'] * 100
                
                # 止损 -2%（做空亏损，即价格上涨2%）
                if price_change <= -2:
                    trades.append({
                        'profit_pct': price_change,
                        'duration_minutes': (row['date'] - position['short_time']).total_seconds() / 60,
                        'exit_reason': 'stop_loss'
                    })
                    position = None
                
                # 止盈 +2%（做空盈利，即价格下跌2%）
                elif price_change >= 2:
                    trades.append({
                        'profit_pct': price_change,
                        'duration_minutes': (row['date'] - position['short_time']).total_seconds() / 60,
                        'exit_reason': 'take_profit'
                    })
                    position = None
                
                # RSI平仓信号
                elif current_rsi < cover_threshold:
                    trades.append({
                        'profit_pct': price_change,
                        'duration_minutes': (row['date'] - position['short_time']).total_seconds() / 60,
                        'exit_reason': 'rsi_cover'
                    })
                    position = None
        
        if len(trades) > 0:
            trades_df = pd.DataFrame(trades)
            
            total_profit = trades_df['profit_pct'].sum()
            win_rate = len(trades_df[trades_df['profit_pct'] > 0]) / len(trades_df) * 100
            avg_profit = trades_df['profit_pct'].mean()
            
            exit_stats = trades_df['exit_reason'].value_counts()
            
            results.append({
                'short_threshold': short_threshold,
                'cover_threshold': cover_threshold,
                'total_trades': len(trades),
                'total_profit': total_profit,
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'avg_duration': trades_df['duration_minutes'].mean(),
                'stop_loss_exits': exit_stats.get('stop_loss', 0),
                'take_profit_exits': exit_stats.get('take_profit', 0),
                'rsi_cover_exits': exit_stats.get('rsi_cover', 0)
            })
            
            print(f"  交易次数: {len(trades)}")
            print(f"  总盈利: {total_profit:.2f}%")
            print(f"  胜率: {win_rate:.1f}%")
            print(f"  平均盈利: {avg_profit:.2f}%")
            print(f"  出场原因: 止损{exit_stats.get('stop_loss', 0)}次, 止盈{exit_stats.get('take_profit', 0)}次, RSI平仓{exit_stats.get('rsi_cover', 0)}次")
        else:
            print("  无交易")
    
    if results:
        results_df = pd.DataFrame(results)
        best_results = results_df.sort_values('total_profit', ascending=False)
        
        print("\n=== 做空策略测试结果（按总盈利排序）===")
        print(best_results.to_string(index=False))
        
        if len(best_results) > 0:
            best = best_results.iloc[0]
            print(f"\n=== 最佳做空策略 ===")
            print(f"做空阈值: RSI > {best['short_threshold']}")
            print(f"平仓阈值: RSI < {best['cover_threshold']}")
            print(f"总盈利: {best['total_profit']:.2f}%")
            print(f"胜率: {best['win_rate']:.1f}%")
            
            return best
    
    return None

if __name__ == '__main__':
    analyze_short_strategy()