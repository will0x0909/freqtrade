#!/usr/bin/env python3
"""
分析代币基础信息与回测表现的关联性
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

def load_token_data():
    """加载代币基础信息"""
    with open('token_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['data']

def load_backtest_results():
    """从Markdown报告中提取回测结果"""
    # 先尝试读取最新的报告文件
    backtest_dir = Path('batch_backtest_results')
    if not backtest_dir.exists():
        print("❌ 未找到回测结果目录")
        return []
    
    # 找到最新的报告文件
    report_files = list(backtest_dir.glob('batch_backtest_report_*.md'))
    if not report_files:
        print("❌ 未找到回测报告文件")
        return []
    
    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
    print(f"📖 读取回测报告: {latest_report}")
    
    # 解析Markdown中的结果表格
    results = []
    with open(latest_report, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找完整结果列表的表格
    lines = content.split('\n')
    in_results_table = False
    
    for line in lines:
        if '## 📋 完整结果列表' in line:
            in_results_table = True
            continue
        
        if in_results_table and line.startswith('|') and not line.startswith('|---'):
            # 跳过表头
            if '代币' in line and '总利润%' in line:
                continue
                
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 7:
                try:
                    pair = parts[0]
                    profit_pct = float(parts[1].replace('%', ''))
                    trades = int(parts[2])
                    win_rate = float(parts[3].replace('%', ''))
                    avg_profit = float(parts[4].replace('%', ''))
                    profit_factor = float(parts[5])
                    expectancy = float(parts[6])
                    
                    results.append({
                        'pair': pair,
                        'symbol': pair.split('/')[0],  # 提取代币符号
                        'profit_pct': profit_pct,
                        'trades': trades,
                        'win_rate': win_rate,
                        'avg_profit': avg_profit,
                        'profit_factor': profit_factor,
                        'expectancy': expectancy
                    })
                except (ValueError, IndexError):
                    continue
        
        # 如果遇到下一个章节，停止解析
        if in_results_table and line.startswith('## ') and '完整结果列表' not in line:
            break
    
    print(f"✅ 解析到 {len(results)} 个回测结果")
    return results

def match_tokens_with_backtest(token_data, backtest_results):
    """匹配代币基础信息与回测结果"""
    # 创建符号到回测结果的映射
    backtest_map = {result['symbol']: result for result in backtest_results}
    
    matched_data = []
    for token in token_data:
        symbol = token['symbol']
        if symbol in backtest_map:
            backtest = backtest_map[symbol]
            
            # 合并数据
            combined = {
                'symbol': symbol,
                'name': token['name'],
                # 基础信息
                'price': float(token['price']),
                'market_cap': float(token['marketCap']),
                'fdv': float(token['fdv']),
                'volume_24h': float(token['volume24h']),
                'percent_change_24h': float(token['percentChange24h']),
                'total_supply': float(token['totalSupply']),
                'circulating_supply': float(token['circulatingSupply']),
                'holders': int(token['holders']),
                'liquidity': float(token['liquidity']),
                'score': int(token['score']),
                'listing_time': int(token['listingTime']),
                # 回测结果
                'profit_pct': backtest['profit_pct'],
                'trades': backtest['trades'],
                'win_rate': backtest['win_rate'],
                'avg_profit': backtest['avg_profit'],
                'profit_factor': backtest['profit_factor'],
                'expectancy': backtest['expectancy']
            }
            matched_data.append(combined)
    
    print(f"✅ 匹配到 {len(matched_data)} 个代币的完整数据")
    return matched_data

def analyze_correlations(df):
    """分析各指标之间的相关性"""
    print("\n🔍 相关性分析:")
    
    # 只使用事前可知的基础指标
    fundamental_metrics = [
        'market_cap', 'fdv', 'volume_24h', 'percent_change_24h',
        'holders', 'liquidity', 'score', 'profit_pct', 'listing_time',
        'circulating_supply'
    ]
    
    # 计算相关系数
    correlation_matrix = df[fundamental_metrics].corr(method='pearson')
    
    # 找出与回测表现最相关的基础指标
    profit_correlations = correlation_matrix['profit_pct'].sort_values(key=abs, ascending=False)
    
    print("\n📊 基础指标与总利润的相关性（事前可知）:")
    for metric, corr in profit_correlations.items():
        if metric != 'profit_pct':
            print(f"   {metric}: {corr:.3f}")
    
    return correlation_matrix

def categorize_performance(df):
    """按表现分类代币并分析各类别特征"""
    # 按利润分类
    df['performance_category'] = pd.cut(
        df['profit_pct'], 
        bins=[-np.inf, -5, 0, 5, np.inf],
        labels=['Poor', 'Below Average', 'Above Average', 'Excellent']
    )
    
    print("\n📈 表现分类统计（使用中位数更有代表性）:")
    category_stats = df.groupby('performance_category', observed=True).agg({
        'profit_pct': ['count', 'median'],
        'market_cap': ['median', 'mean'],
        'holders': ['median', 'mean'], 
        'score': ['median', 'mean'],
        'liquidity': ['median', 'mean'],
        'volume_24h': ['median', 'mean']
    }).round(2)
    
    print(category_stats)
    
    # 额外显示关键指标的分位数信息
    print("\n📊 各类别关键指标分位数:")
    for category in df['performance_category'].cat.categories:
        cat_data = df[df['performance_category'] == category]
        if len(cat_data) > 0:
            print(f"\n{category} ({len(cat_data)}个代币):")
            print(f"  利润: 25%={cat_data['profit_pct'].quantile(0.25):.2f}%, 中位数={cat_data['profit_pct'].median():.2f}%, 75%={cat_data['profit_pct'].quantile(0.75):.2f}%")
            print(f"  市值: 中位数=${cat_data['market_cap'].median():,.0f}, 均值=${cat_data['market_cap'].mean():,.0f}")
            print(f"  流动性: 中位数=${cat_data['liquidity'].median():,.0f}, 均值=${cat_data['liquidity'].mean():,.0f}")
            print(f"  持有者: 中位数={cat_data['holders'].median():.0f}, 均值={cat_data['holders'].mean():.0f}")
    
    return df

def find_top_performers_characteristics(df):
    """分析顶级表现者的特征"""
    print("\n🏆 顶级表现者 (利润>5%) 特征:")
    top_performers = df[df['profit_pct'] > 5].sort_values('profit_pct', ascending=False)
    
    if len(top_performers) > 0:
        print(f"数量: {len(top_performers)}")
        print(f"中位数市值: ${top_performers['market_cap'].median():,.0f} (均值: ${top_performers['market_cap'].mean():,.0f})")
        print(f"中位数持有者: {top_performers['holders'].median():.0f} (均值: {top_performers['holders'].mean():.0f})")
        print(f"中位数评分: {top_performers['score'].median():.0f} (均值: {top_performers['score'].mean():.0f})")
        print(f"中位数流动性: ${top_performers['liquidity'].median():,.0f} (均值: ${top_performers['liquidity'].mean():,.0f})")
        print(f"中位数交易量: ${top_performers['volume_24h'].median():,.0f} (均值: ${top_performers['volume_24h'].mean():,.0f})")
        
        print("\n🎯 具体代币:")
        for _, token in top_performers.iterrows():
            print(f"   {token['symbol']}: {token['profit_pct']:.2f}% (市值: ${token['market_cap']:,.0f}, 持有者: {token['holders']}, 评分: {token['score']})")
    
    return top_performers

def main():
    print("🔗 开始分析代币基础信息与回测表现的关联性...")
    
    # 加载数据
    print("📥 加载代币基础信息...")
    token_data = load_token_data()
    print(f"✅ 加载了 {len(token_data)} 个代币的基础信息")
    
    print("\n📥 加载回测结果...")
    backtest_results = load_backtest_results()
    
    if not backtest_results:
        print("❌ 无法加载回测结果")
        return
    
    # 匹配数据
    print("\n🔗 匹配代币信息与回测结果...")
    matched_data = match_tokens_with_backtest(token_data, backtest_results)
    
    if not matched_data:
        print("❌ 没有匹配的数据")
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(matched_data)
    
    # 基础统计
    print(f"\n📊 数据概览:")
    print(f"匹配的代币数量: {len(df)}")
    print(f"市值: 中位数=${df['market_cap'].median():,.0f}, 均值=${df['market_cap'].mean():,.0f}")
    print(f"利润: 中位数={df['profit_pct'].median():.2f}%, 均值={df['profit_pct'].mean():.2f}%")
    print(f"盈利代币数量: {len(df[df['profit_pct'] > 0])} ({len(df[df['profit_pct'] > 0])/len(df)*100:.1f}%)")
    print(f"流动性: 中位数=${df['liquidity'].median():,.0f}, 均值=${df['liquidity'].mean():,.0f}")
    print(f"持有者: 中位数={df['holders'].median():.0f}, 均值={df['holders'].mean():.0f}")
    
    # 相关性分析
    correlation_matrix = analyze_correlations(df)
    
    # 表现分类
    df = categorize_performance(df)
    
    # 顶级表现者分析
    top_performers = find_top_performers_characteristics(df)
    
    # 保存结果
    output_file = 'token_correlation_analysis.json'
    analysis_results = {
        'summary': {
            'total_tokens': len(df),
            'profitable_tokens': len(df[df['profit_pct'] > 0]),
            'avg_profit': df['profit_pct'].mean(),
            'avg_market_cap': df['market_cap'].mean()
        },
        'top_performers': top_performers.to_dict('records') if len(top_performers) > 0 else [],
        'correlations': correlation_matrix['profit_pct'].to_dict()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 分析结果已保存到: {output_file}")
    print("📊 可以使用这些数据来选择有潜力的代币进行策略优化")
    
    # 输出实用的选币建议
    print("\n🎯 基于基础面的选币建议（事前可知指标）:")
    print("✅ 优质代币特征:")
    print("   - Binance评分 > 70分")
    print("   - 持有者数量 > 20,000人") 
    print("   - 市值在$10M-$100M区间")
    print("   - 24小时交易量适中（流动性好但非过热）")
    print("   - 流动性 > $1M")
    
    print("\n❌ 避免的代币特征:")
    print("   - Binance评分 < 30分")
    print("   - 持有者数量 < 5,000人")
    print("   - 市值过小（< $1M）或过大（> $500M）")
    print("   - 流动性不足（< $100K）")
    
    # 生成推荐代币列表
    print("\n🎯 基于分析的推荐代币筛选:")
    recommended = df[
        (df['liquidity'] > 1000000) &  # 流动性 > $1M
        (df['holders'] > 10000) &      # 持有者 > 10K
        (df['score'] > 50) &           # 评分 > 50
        (df['market_cap'] > 5000000) & # 市值 > $5M
        (df['market_cap'] < 200000000) # 市值 < $200M
    ].sort_values('profit_pct', ascending=False)
    
    print(f"符合条件的代币数量: {len(recommended)}")
    if len(recommended) > 0:
        print("推荐代币（按回测表现排序）:")
        for _, token in recommended.head(10).iterrows():
            print(f"   {token['symbol']}: {token['profit_pct']:.2f}% (流动性: ${token['liquidity']:,.0f}, 持有者: {token['holders']}, 评分: {token['score']})")
        
        # 保存推荐列表
        recommended_pairs = recommended['symbol'].tolist()
        print(f"\n推荐代币列表: {recommended_pairs[:10]}")
        
        # 生成freqtrade命令
        if len(recommended_pairs) > 0:
            pairs_str = ','.join([f"{symbol}/USDT" for symbol in recommended_pairs[:10]])
            print(f"\n💡 推荐的freqtrade回测命令:")
            print(f"freqtrade backtesting -c user_data/config_alpha.json --strategy UniversalMACD1m --fee 0.001 --timeframe 1m --pairs {pairs_str}")
    else:
        print("❌ 没有符合所有筛选条件的代币")

if __name__ == "__main__":
    main()