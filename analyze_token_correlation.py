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

def calculate_dynamic_thresholds(df):
    """基于数据分布计算动态阈值"""
    thresholds = {}
    
    # 利润分类阈值 - 使用四分位数
    profit_q25 = df['profit_pct'].quantile(0.25)
    profit_q50 = df['profit_pct'].quantile(0.50)  # 中位数
    profit_q75 = df['profit_pct'].quantile(0.75)
    
    thresholds['profit_categories'] = [
        -np.inf, profit_q25, profit_q50, profit_q75, np.inf
    ]
    
    # 顶级表现者阈值 - 使用90分位数
    thresholds['top_performer_threshold'] = df['profit_pct'].quantile(0.90)
    
    # 筛选条件阈值 - 使用合理的百分位数
    thresholds['filtering'] = {
        'liquidity_min': df['liquidity'].quantile(0.7),  # 70分位数
        'holders_min': df['holders'].quantile(0.6),      # 60分位数  
        'score_min': df['score'].quantile(0.4),          # 40分位数
        'market_cap_min': df['market_cap'].quantile(0.3), # 30分位数
        'market_cap_max': df['market_cap'].quantile(0.8)  # 80分位数
    }
    
    # 建议阈值 - 基于数据分布的更严格标准
    thresholds['recommendations'] = {
        'score_good': df['score'].quantile(0.8),         # 好的评分
        'score_bad': df['score'].quantile(0.2),          # 差的评分
        'holders_good': df['holders'].quantile(0.75),    # 好的持有者数量
        'holders_bad': df['holders'].quantile(0.25),     # 差的持有者数量
        'market_cap_good_min': df['market_cap'].quantile(0.2),
        'market_cap_good_max': df['market_cap'].quantile(0.7),
        'market_cap_bad_min': df['market_cap'].quantile(0.05),
        'market_cap_bad_max': df['market_cap'].quantile(0.95),
        'liquidity_good': df['liquidity'].quantile(0.8),
        'liquidity_bad': df['liquidity'].quantile(0.15)
    }
    
    return thresholds

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

def analyze_data_distribution(df):
    """分析数据分布以确定合理阈值"""
    print("\n📊 数据分布分析:")
    
    key_metrics = ['profit_pct', 'market_cap', 'holders', 'liquidity', 'score']
    
    for metric in key_metrics:
        data = df[metric]
        print(f"\n{metric}:")
        print(f"  范围: {data.min():.2f} - {data.max():.2f}")
        print(f"  中位数: {data.median():.2f}")
        print(f"  均值: {data.mean():.2f}")
        print(f"  标准差: {data.std():.2f}")
        print(f"  25%分位数: {data.quantile(0.25):.2f}")
        print(f"  75%分位数: {data.quantile(0.75):.2f}")
        print(f"  90%分位数: {data.quantile(0.90):.2f}")
    
    return True

def categorize_performance(df, thresholds=None):
    """按表现分类代币并分析各类别特征"""
    if thresholds is None:
        # 使用默认硬编码阈值（向后兼容）
        bins = [-np.inf, -5, 0, 5, np.inf]
    else:
        # 使用动态计算的阈值
        bins = thresholds['profit_categories']
        print(f"\n📈 使用动态阈值进行分类: {[f'{x:.2f}' if x != -np.inf and x != np.inf else str(x) for x in bins]}")
    
    # 按利润分类
    df['performance_category'] = pd.cut(
        df['profit_pct'], 
        bins=bins,
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

def find_top_performers_characteristics(df, thresholds=None):
    """分析顶级表现者的特征"""
    if thresholds is None:
        threshold = 5  # 默认硬编码阈值
    else:
        threshold = thresholds['top_performer_threshold']
    
    print(f"\n🏆 顶级表现者 (利润>{threshold:.2f}%) 特征:")
    top_performers = df[df['profit_pct'] > threshold].sort_values('profit_pct', ascending=False)
    
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
    
    # 数据分布分析
    analyze_data_distribution(df)
    
    # 计算动态阈值
    print("\n🔧 计算动态阈值...")
    thresholds = calculate_dynamic_thresholds(df)
    
    # 相关性分析
    correlation_matrix = analyze_correlations(df)
    
    # 表现分类 - 使用动态阈值
    df = categorize_performance(df, thresholds)
    
    # 顶级表现者分析 - 使用动态阈值
    top_performers = find_top_performers_characteristics(df, thresholds)
    
    # 保存结果
    output_file = 'token_correlation_analysis.json'
    analysis_results = {
        'summary': {
            'total_tokens': len(df),
            'profitable_tokens': len(df[df['profit_pct'] > 0]),
            'avg_profit': df['profit_pct'].mean(),
            'avg_market_cap': df['market_cap'].mean()
        },
        'dynamic_thresholds': {
            'profit_categories': thresholds['profit_categories'],
            'top_performer_threshold': thresholds['top_performer_threshold'],
            'filtering_criteria': thresholds['filtering'],
            'recommendations': thresholds['recommendations']
        },
        'top_performers': top_performers.to_dict('records') if len(top_performers) > 0 else [],
        'correlations': correlation_matrix['profit_pct'].to_dict()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 分析结果已保存到: {output_file}")
    print("📊 可以使用这些数据来选择有潜力的代币进行策略优化")
    
    # 使用动态阈值输出选币建议
    print("\n🎯 基于数据分析的选币建议（事前可知指标）:")
    print("✅ 优质代币特征:")
    print(f"   - Binance评分 > {thresholds['recommendations']['score_good']:.0f}分")
    print(f"   - 持有者数量 > {thresholds['recommendations']['holders_good']:,.0f}人") 
    print(f"   - 市值在${thresholds['recommendations']['market_cap_good_min']:,.0f}-${thresholds['recommendations']['market_cap_good_max']:,.0f}区间")
    print(f"   - 流动性 > ${thresholds['recommendations']['liquidity_good']:,.0f}")
    
    print("\n❌ 避免的代币特征:")
    print(f"   - Binance评分 < {thresholds['recommendations']['score_bad']:.0f}分")
    print(f"   - 持有者数量 < {thresholds['recommendations']['holders_bad']:,.0f}人")
    print(f"   - 市值过小（< ${thresholds['recommendations']['market_cap_bad_min']:,.0f}）或过大（> ${thresholds['recommendations']['market_cap_bad_max']:,.0f}）")
    print(f"   - 流动性不足（< ${thresholds['recommendations']['liquidity_bad']:,.0f}）")
    
    # 生成推荐代币列表 - 使用动态阈值
    print("\n🎯 基于动态分析的推荐代币筛选:")
    recommended = df[
        (df['liquidity'] > thresholds['filtering']['liquidity_min']) &
        (df['holders'] > thresholds['filtering']['holders_min']) &
        (df['score'] > thresholds['filtering']['score_min']) &
        (df['market_cap'] > thresholds['filtering']['market_cap_min']) &
        (df['market_cap'] < thresholds['filtering']['market_cap_max'])
    ].sort_values('profit_pct', ascending=False)
    
    print(f"筛选条件:")
    print(f"  - 流动性 > ${thresholds['filtering']['liquidity_min']:,.0f}")
    print(f"  - 持有者 > {thresholds['filtering']['holders_min']:,.0f}")
    print(f"  - 评分 > {thresholds['filtering']['score_min']:.0f}")
    print(f"  - 市值 ${thresholds['filtering']['market_cap_min']:,.0f} - ${thresholds['filtering']['market_cap_max']:,.0f}")
    
    print(f"符合条件的代币数量: {len(recommended)}")
    if len(recommended) > 0:
        print("推荐代币（按回测表现排序）:")
        for _, token in recommended.iterrows():
            print(f"   {token['symbol']}: {token['profit_pct']:.2f}% (流动性: ${token['liquidity']:,.0f}, 持有者: {token['holders']}, 评分: {token['score']})")
        
        # 保存推荐列表
        recommended_pairs = recommended['symbol'].tolist()
        print(f"\n推荐代币列表: {recommended_pairs[:10]}")
        
        # 生成freqtrade命令
        if len(recommended_pairs) > 0:
            pairs_str = ' '.join([f"{symbol}/USDT" for symbol in recommended_pairs])
            print(f"\n💡 推荐的freqtrade回测命令:")
            print(f"freqtrade backtesting -c user_data/config_alpha.json --strategy UniversalMACD1m --fee 0.001 --timeframe 1m --pairs {pairs_str}")
    else:
        print("❌ 没有符合所有筛选条件的代币")

if __name__ == "__main__":
    main()