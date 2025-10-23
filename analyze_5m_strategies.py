#!/usr/bin/env python3
"""
Analyze 5m strategy performance from strategy_test_report.md
"""
import re
from collections import defaultdict
import pandas as pd


def parse_strategy_report():
    """Parse the strategy test report and extract 5m data"""
    
    with open('strategy_test_report.md', 'r') as f:
        content = f.read()
    
    # Find the summary table section
    lines = content.split('\n')
    
    # Find the table header
    table_start = None
    for i, line in enumerate(lines):
        if '| Token | Strategy | Timeframe | Total Profit (%) | Total Trades | Win Rate (%) | Max Drawdown (%) | Status |' in line:
            table_start = i + 2  # Skip header and separator
            break
    
    if table_start is None:
        print("Could not find table header")
        return None
    
    # Parse only 5m data
    strategy_data = defaultdict(list)
    
    for line in lines[table_start:]:
        if not line.strip() or not line.startswith('|'):
            continue
            
        parts = [p.strip() for p in line.split('|')[1:-1]]  # Remove empty first/last elements
        
        if len(parts) < 7:
            continue
            
        token, strategy, timeframe, profit, trades, win_rate, drawdown, status = parts
        
        # Only process 5m timeframe and successful runs
        if timeframe == '5m' and status == '✅ Success':
            # Skip entries with N/A values
            if profit == 'N/A' or trades == 'N/A':
                continue
                
            try:
                profit_val = float(profit) if profit != 'N/A' else 0.0
                trades_val = int(trades) if trades != 'N/A' else 0
                win_rate_val = float(win_rate) if win_rate != 'N/A' else 0.0
                drawdown_val = float(drawdown) if drawdown != 'N/A' else 0.0
                
                strategy_data[strategy].append({
                    'token': token,
                    'profit': profit_val,
                    'trades': trades_val,
                    'win_rate': win_rate_val,
                    'drawdown': drawdown_val
                })
            except ValueError:
                continue
    
    return strategy_data


def calculate_strategy_stats(strategy_data):
    """Calculate statistics for each strategy"""
    
    stats = []
    
    for strategy, data in strategy_data.items():
        if not data:
            continue
            
        profits = [d['profit'] for d in data]
        trades = [d['trades'] for d in data]
        win_rates = [d['win_rate'] for d in data if d['trades'] > 0]  # Only count where trades happened
        drawdowns = [d['drawdown'] for d in data if d['drawdown'] > 0]  # Only count non-zero drawdowns
        
        # Count tokens with profits > 0, < 0, and = 0
        profitable_tokens = len([p for p in profits if p > 0])
        losing_tokens = len([p for p in profits if p < 0])
        neutral_tokens = len([p for p in profits if p == 0])
        
        # Count tokens with trades
        tokens_with_trades = len([t for t in trades if t > 0])
        
        stats.append({
            'strategy': strategy,
            'total_tokens': len(data),
            'tokens_with_trades': tokens_with_trades,
            'profitable_tokens': profitable_tokens,
            'losing_tokens': losing_tokens,
            'neutral_tokens': neutral_tokens,
            'avg_profit': sum(profits) / len(profits),
            'median_profit': sorted(profits)[len(profits)//2],
            'max_profit': max(profits),
            'min_profit': min(profits),
            'total_trades': sum(trades),
            'avg_trades_per_token': sum(trades) / len(trades),
            'avg_win_rate': sum(win_rates) / len(win_rates) if win_rates else 0,
            'avg_drawdown': sum(drawdowns) / len(drawdowns) if drawdowns else 0,
            'max_drawdown': max(drawdowns) if drawdowns else 0,
            'profitability_rate': profitable_tokens / len(data) * 100,
        })
    
    return sorted(stats, key=lambda x: x['avg_profit'], reverse=True)

def generate_markdown_report(stats):
    """Generate markdown report"""
    from datetime import datetime
    
    profitable_stats = sorted(stats, key=lambda x: x['profitability_rate'], reverse=True)
    trade_stats = sorted(stats, key=lambda x: x['total_trades'], reverse=True)
    
    all_profits = [stat['avg_profit'] for stat in stats]
    all_trades = [stat['total_trades'] for stat in stats]
    strategies_with_positive_avg = len([stat for stat in stats if stat['avg_profit'] > 0])
    
    report = f"""# 5分钟时间框架策略表现分析报告

**分析时间**: {datetime.now().strftime('%Y-%m-%d')}  
**数据源**: strategy_test_report.md  
**分析范围**: 49个代币，{len(stats)}个策略，5分钟时间框架  

---

## 📊 总体概况

- **策略总数**: {len(stats)}个
- **测试代币**: 49个 (来自 1_m_listing_tokens.csv)
- **测试周期**: 每个代币上市后14天
- **总交易数**: {sum(all_trades):,}笔
- **平均收益率为正的策略**: {strategies_with_positive_avg}个 ({strategies_with_positive_avg/len(stats)*100:.1f}%)
- **整体平均收益率**: {sum(all_profits)/len(all_profits):.2f}%
- **平均每策略交易数**: {sum(all_trades)/len(all_trades):.1f}笔

---

## 🏆 最佳表现策略排行榜

### 按平均收益率排序 (全部策略)

| 排名 | 策略名称 | 测试代币数 | 有交易代币 | 盈利代币 | 亏损代币 | 平均收益率 | 总交易数 | 平均胜率 | 最大回撤 |
|------|----------|------------|------------|----------|----------|------------|----------|----------|----------|
"""
    
    for i, stat in enumerate(stats):
        report += f"| {i+1} | **{stat['strategy']}** | {stat['total_tokens']} | {stat['tokens_with_trades']} | {stat['profitable_tokens']} | {stat['losing_tokens']} | **{stat['avg_profit']:.2f}%** | {stat['total_trades']} | {stat['avg_win_rate']:.1f}% | {stat['avg_drawdown']:.2f}% |\n"
    
    report += """
---

## 📈 盈利稳定性排行榜

### 按盈利代币比例排序 (全部策略)

| 排名 | 策略名称 | 盈利比例 | 盈利代币数 | 总代币数 | 平均收益率 | 总交易数 |
|------|----------|----------|------------|----------|------------|----------|
"""
    
    for i, stat in enumerate(profitable_stats):
        report += f"| {i+1} | **{stat['strategy']}** | **{stat['profitability_rate']:.1f}%** | {stat['profitable_tokens']} | {stat['total_tokens']} | {stat['avg_profit']:.2f}% | {stat['total_trades']} |\n"
    
    report += """
---

## 📊 交易活跃度排行榜

### 按总交易数排序 (全部策略)

| 排名 | 策略名称 | 总交易数 | 有交易代币数 | 平均每币交易数 | 平均胜率 |
|------|----------|----------|--------------|----------------|----------|
"""
    
    for i, stat in enumerate(trade_stats):
        report += f"| {i+1} | **{stat['strategy']}** | **{stat['total_trades']:,}** | {stat['tokens_with_trades']} | {stat['avg_trades_per_token']:.1f} | {stat['avg_win_rate']:.1f}% |\n"
    
    # Find best strategies for recommendations
    best_balanced = stats[0]  # Best by avg profit
    best_stable = profitable_stats[0]  # Best by profitability rate
    
    report += f"""
---

## 💡 关键洞察与发现

### 🌟 最佳综合表现策略

1. **{best_balanced['strategy']}**
   - ✅ 平均收益率: {best_balanced['avg_profit']:.2f}%
   - ✅ 盈利稳定性: {best_balanced['profitability_rate']:.1f}% ({best_balanced['profitable_tokens']}/{best_balanced['total_tokens']}代币盈利)
   - ✅ 平均胜率: {best_balanced['avg_win_rate']:.1f}%
   - ✅ 最大回撤: {best_balanced['avg_drawdown']:.2f}%

2. **{best_stable['strategy']}**
   - ✅ 最高盈利稳定性: {best_stable['profitability_rate']:.1f}%代币盈利
   - ✅ 平均收益率: {best_stable['avg_profit']:.2f}%
   - ✅ 平均胜率: {best_stable['avg_win_rate']:.1f}%
   - ✅ 总交易数: {best_stable['total_trades']}笔

### 📉 市场环境分析

- **整体表现偏弱**: {100-strategies_with_positive_avg/len(stats)*100:.1f}%的策略平均收益为负，反映出新上市代币的高波动性和不确定性
- **高频交易vs稳定收益**: 交易最活跃的策略({trade_stats[0]['strategy']})并非收益最高
- **胜率与收益率不完全正相关**: 需要综合考虑交易频率、盈亏比等因素

### 🎯 策略选择建议

#### 适合稳健投资者
- **{profitable_stats[0]['strategy']}**: 最高盈利稳定性 ({profitable_stats[0]['profitability_rate']:.1f}%代币盈利)
- **{profitable_stats[1]['strategy']}**: 次高稳定性 ({profitable_stats[1]['profitability_rate']:.1f}%代币盈利)

#### 适合激进投资者  
- **{stats[0]['strategy']}**: 最高平均收益率 ({stats[0]['avg_profit']:.2f}%)
- **{stats[1]['strategy']}**: 次高收益率 ({stats[1]['avg_profit']:.2f}%)

---

## 📋 方法论说明

**数据处理**:
- 仅分析5分钟时间框架数据
- 排除失败运行和无交易数据
- 基于49个新上市代币的14天测试周期

**评估指标**:
- **平均收益率**: 所有代币收益率的算术平均
- **盈利稳定性**: 盈利代币数占总测试代币数的比例
- **胜率**: 盈利交易占总交易数的比例
- **最大回撤**: 策略在测试期间的最大亏损幅度

**局限性**:
- 测试周期相对较短(14天)
- 样本偏向新上市代币，可能存在选择偏差
- 未考虑交易成本和滑点影响

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*数据分析工具: Python*
"""
    
    return report

def main():
    print("Analyzing 5m strategy performance...")
    
    strategy_data = parse_strategy_report()
    if not strategy_data:
        print("Failed to parse strategy data")
        return
    
    stats = calculate_strategy_stats(strategy_data)
    
    # Generate and save markdown report
    report = generate_markdown_report(stats)
    
    output_file = '5m_strategy_analysis.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"分析完成! 报告已保存到: {output_file}")
    
    # Also print summary to console
    print(f"\n5m策略统计分析结果 (共 {len(stats)} 个策略)")
    print("=" * 80)
    
    print("\n🏆 前5个最佳策略 (按平均收益率):")
    for i, stat in enumerate(stats[:5]):
        print(f"{i+1}. {stat['strategy']}: {stat['avg_profit']:.2f}% (盈利率: {stat['profitability_rate']:.1f}%)")
    
    profitable_stats = sorted(stats, key=lambda x: x['profitability_rate'], reverse=True)
    print("\n📈 前5个最稳定策略 (按盈利代币比例):")
    for i, stat in enumerate(profitable_stats[:5]):
        print(f"{i+1}. {stat['strategy']}: {stat['profitability_rate']:.1f}% ({stat['profitable_tokens']}/{stat['total_tokens']})")
    
    all_profits = [stat['avg_profit'] for stat in stats]
    all_trades = [stat['total_trades'] for stat in stats]
    strategies_with_positive_avg = len([stat for stat in stats if stat['avg_profit'] > 0])
    
    print(f"\n📋 整体统计:")
    print(f"- 平均收益率为正的策略: {strategies_with_positive_avg}/{len(stats)} ({strategies_with_positive_avg/len(stats)*100:.1f}%)")
    print(f"- 所有策略平均收益率: {sum(all_profits)/len(all_profits):.2f}%")
    print(f"- 总交易数: {sum(all_trades):,}笔")

if __name__ == "__main__":
    main()