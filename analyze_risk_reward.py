#!/usr/bin/env python3
"""
分析CYC/USDT的最佳风险收益比
"""

import pandas as pd
import numpy as np
import talib.abstract as ta

def analyze_risk_reward():
    df = pd.read_feather('user_data/data/binance/CYC_USDT-5m.feather')
    df['rsi'] = ta.RSI(df, timeperiod=14)
    
    print(f"数据加载成功，共{len(df)}条记录")
    
    # 测试不同的风险收益比
    risk_reward_tests = [
        (-1, 2),   # 1:2
        (-1, 3),   # 1:3  
        (-1.5, 3), # 1.5:3 = 1:2
        (-1.5, 4.5), # 1.5:4.5 = 1:3
        (-2, 4),   # 2:4 = 1:2
        (-2, 6),   # 2:6 = 1:3 (当前)
        (-3, 6),   # 3:6 = 1:2
        (-3, 9),   # 3:9 = 1:3
        (-0.5, 1), # 0.5:1 = 1:2 (更小止损)
        (-0.5, 1.5), # 0.5:1.5 = 1:3
    ]
    
    results = []
    
    for stop_loss_pct, take_profit_pct in risk_reward_tests:
        print(f"\n测试风险收益比: {stop_loss_pct}% : {take_profit_pct}%")
        
        # 使用最优RSI参数: 14期, 买入<30, 卖出>70
        position = None
        trades = []
        
        for i, row in df.iterrows():
            if pd.isna(row['rsi']):
                continue
                
            current_price = row['close']
            current_rsi = row['rsi']
            
            # 买入信号
            if position is None and current_rsi < 30:
                position = {
                    'buy_price': current_price,
                    'buy_time': row['date'],
                }
            
            # 卖出信号
            elif position is not None:
                price_change = (current_price - position['buy_price']) / position['buy_price'] * 100
                
                # 止损
                if price_change <= stop_loss_pct:
                    trades.append({
                        'profit_pct': price_change,
                        'duration_minutes': (row['date'] - position['buy_time']).total_seconds() / 60,
                        'exit_reason': 'stop_loss'
                    })
                    position = None
                
                # 止盈
                elif price_change >= take_profit_pct:
                    trades.append({
                        'profit_pct': price_change,
                        'duration_minutes': (row['date'] - position['buy_time']).total_seconds() / 60,
                        'exit_reason': 'take_profit'
                    })
                    position = None
                
                # RSI卖出信号
                elif current_rsi > 70:
                    trades.append({
                        'profit_pct': price_change,
                        'duration_minutes': (row['date'] - position['buy_time']).total_seconds() / 60,
                        'exit_reason': 'rsi_signal'
                    })
                    position = None
        
        if len(trades) > 0:
            trades_df = pd.DataFrame(trades)
            
            total_profit = trades_df['profit_pct'].sum()
            win_rate = len(trades_df[trades_df['profit_pct'] > 0]) / len(trades_df) * 100
            avg_profit = trades_df['profit_pct'].mean()
            
            # 统计出场原因
            exit_stats = trades_df['exit_reason'].value_counts()
            
            results.append({
                'stop_loss': stop_loss_pct,
                'take_profit': take_profit_pct,
                'risk_reward_ratio': f"1:{abs(take_profit_pct/stop_loss_pct):.1f}",
                'total_trades': len(trades),
                'total_profit': total_profit,
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'avg_duration': trades_df['duration_minutes'].mean(),
                'stop_loss_exits': exit_stats.get('stop_loss', 0),
                'take_profit_exits': exit_stats.get('take_profit', 0),
                'rsi_signal_exits': exit_stats.get('rsi_signal', 0)
            })
            
            print(f"  交易次数: {len(trades)}")
            print(f"  总盈利: {total_profit:.2f}%")
            print(f"  胜率: {win_rate:.1f}%")
            print(f"  平均盈利: {avg_profit:.2f}%")
            print(f"  出场原因: 止损{exit_stats.get('stop_loss', 0)}次, 止盈{exit_stats.get('take_profit', 0)}次, RSI信号{exit_stats.get('rsi_signal', 0)}次")
        else:
            print("  无交易")
    
    # 分析结果
    if results:
        results_df = pd.DataFrame(results)
        best_results = results_df.sort_values('total_profit', ascending=False)
        
        print("\n=== 按总盈利排序的风险收益比测试结果 ===")
        print(best_results.to_string(index=False))
        
        if len(best_results) > 0:
            best = best_results.iloc[0]
            print(f"\n=== 最佳风险收益比 ===")
            print(f"止损: {best['stop_loss']}%")
            print(f"止盈: {best['take_profit']}%") 
            print(f"风险收益比: {best['risk_reward_ratio']}")
            print(f"总盈利: {best['total_profit']:.2f}%")
            print(f"胜率: {best['win_rate']:.1f}%")
            
            return best
    
    return None

if __name__ == '__main__':
    analyze_risk_reward()