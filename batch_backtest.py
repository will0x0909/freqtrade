#!/usr/bin/env python3
"""
批量单币种回测脚本
为配置文件中的每个代币运行单独回测，并分析表现
"""

import json
import subprocess
import time
import os
import re
import zipfile
from pathlib import Path
import pandas as pd
from multiprocessing import Pool, cpu_count, Manager
from functools import partial

def load_pairs_from_config(config_path):
    """从配置文件加载代币列表"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config['exchange']['pair_whitelist']

def run_single_pair_backtest(config_data, pair):
    """为单个代币运行回测"""
    config_path, strategy, fee, timeframe, output_dir, progress_dict = config_data
    
    # 清理代币名称用作文件名
    safe_pair_name = pair.replace('/', '_').replace('\\', '_')
    
    # 为每个代币创建独立的输出目录
    pair_output_dir = os.path.join(output_dir, safe_pair_name)
    os.makedirs(pair_output_dir, exist_ok=True)
    
    # 构建freqtrade命令，移除--backtest-filename让freqtrade自己生成
    cmd = [
        'freqtrade', 'backtesting',
        '-c', config_path,
        '--strategy', strategy,
        '--fee', str(fee),
        '--timeframe', timeframe,
        '--pairs', pair,
        '--export', 'trades',
        '--backtest-directory', pair_output_dir
    ]
    
    try:
        # 运行回测，30秒超时
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # 更新进度
        with progress_dict['lock']:
            progress_dict['completed'] += 1
            completed = progress_dict['completed']
            total = progress_dict['total']
            
        if result.returncode == 0:
            # 在该代币的输出目录中查找结果文件
            result_file_path, meta_path = extract_result_file_path_from_dir(pair_output_dir, result.stderr)
            if result_file_path and os.path.exists(result_file_path):
                if result_file_path.endswith('.zip'):
                    parsed_result = parse_backtest_zip(result_file_path, pair)
                else:
                    parsed_result = parse_backtest_json(result_file_path, pair)
            else:
                parsed_result = {'pair': pair, 'status': 'no_result_file', 'total_trades': 0, 'total_profit_pct': 0.0}
            
            # 显示进度
            if parsed_result and 'total_profit_pct' in parsed_result:
                profit = parsed_result.get('total_profit_pct', 0)
                trades = parsed_result.get('total_trades', 0)
                print(f"✅ [{completed}/{total}] {pair}: {profit:.2f}% ({trades} 笔) - {completed/total*100:.1f}%")
            else:
                print(f"⚠️ [{completed}/{total}] {pair}: 解析失败 - {completed/total*100:.1f}%")
            
            return parsed_result
        else:
            if "No data found" in result.stderr:
                print(f"📭 [{completed}/{total}] {pair}: 无数据 - {completed/total*100:.1f}%")
                return {'pair': pair, 'status': 'no_data', 'total_trades': 0, 'total_profit_pct': 0.0}
            else:
                print(f"❌ [{completed}/{total}] {pair}: 失败 - {completed/total*100:.1f}%")
                return {'pair': pair, 'status': 'failed', 'total_trades': 0, 'total_profit_pct': 0.0}
            
    except subprocess.TimeoutExpired:
        with progress_dict['lock']:
            progress_dict['completed'] += 1
            completed = progress_dict['completed']
            total = progress_dict['total']
        print(f"⏰ [{completed}/{total}] {pair}: 超时(30s) - {completed/total*100:.1f}%")
        return {'pair': pair, 'status': 'timeout', 'total_trades': 0, 'total_profit_pct': 0.0}
    except Exception as e:
        with progress_dict['lock']:
            progress_dict['completed'] += 1
            completed = progress_dict['completed']
            total = progress_dict['total']
        print(f"❌ [{completed}/{total}] {pair}: 出错 - {completed/total*100:.1f}%")
        return {'pair': pair, 'status': 'error', 'error': str(e)[:100], 'total_trades': 0, 'total_profit_pct': 0.0}

def extract_result_file_path(stderr_output):
    """从stderr输出中提取结果文件路径"""
    lines = stderr_output.split('\n')
    for line in lines:
        if 'dumping json to' in line:
            # 提取路径，支持.meta.json
            match = re.search(r'"([^"]*\.meta\.json)"', line)
            if match:
                meta_json_path = match.group(1)
                # 查找对应的zip文件
                zip_path = meta_json_path.replace('.meta.json', '.zip')
                if os.path.exists(zip_path):
                    return zip_path, meta_json_path
                # 如果没有zip，查找普通json
                json_path = meta_json_path.replace('.meta.json', '.json')
                if os.path.exists(json_path):
                    return json_path, meta_json_path
    return None, None

def extract_result_file_path_from_dir(output_dir, stderr_output):
    """从指定目录中查找最新的回测结果文件"""
    try:
        # 首先尝试从stderr输出中提取路径
        result_path, meta_path = extract_result_file_path(stderr_output)
        if result_path:
            return result_path, meta_path
        
        # 如果没有找到，在输出目录中查找最新的文件
        files = []
        for file in os.listdir(output_dir):
            if file.endswith('.zip') or file.endswith('.json'):
                if not file.endswith('.meta.json'):  # 排除meta文件
                    file_path = os.path.join(output_dir, file)
                    if os.path.isfile(file_path):
                        files.append((file_path, os.path.getmtime(file_path)))
        
        if files:
            # 按修改时间排序，返回最新的文件
            files.sort(key=lambda x: x[1], reverse=True)
            newest_file = files[0][0]
            if newest_file.endswith('.zip'):
                return newest_file, None
            else:
                return newest_file, None
        
        return None, None
    except Exception as e:
        print(f"❌ 查找结果文件时出错: {e}")
        return None, None

def parse_backtest_zip(zip_file_path, pair):
    """从ZIP文件解析回测结果"""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            # 查找JSON文件
            json_files = [f for f in zip_file.namelist() if f.endswith('.json')]
            if not json_files:
                return {'pair': pair, 'total_trades': 0, 'total_profit_pct': 0.0}
            
            # 读取第一个JSON文件
            with zip_file.open(json_files[0]) as f:
                data = json.load(f)
        
        strategy_data = data.get('strategy', {})
        if not strategy_data:
            return {'pair': pair, 'total_trades': 0, 'total_profit_pct': 0.0}
        
        # 查找对应代币的数据，或使用TOTAL数据
        pair_data = None
        for key, value in strategy_data.items():
            if isinstance(value, dict) and ('results_per_pair' in value or 'results_per_enter_tag' in value):
                results_per_pair = value.get('results_per_pair', [])
                # 寻找具体代币的数据
                for result in results_per_pair:
                    if result.get('key') == pair:
                        pair_data = result
                        break
                
                # 如果没找到具体代币，使用TOTAL数据
                if not pair_data:
                    for result in results_per_pair:
                        if result.get('key') == 'TOTAL':
                            pair_data = result
                            break
                
                if pair_data:
                    break
        
        if not pair_data:
            return {'pair': pair, 'total_trades': 0, 'total_profit_pct': 0.0}
        
        return {
            'pair': pair,
            'total_trades': pair_data.get('trades', 0),
            'avg_profit_pct': pair_data.get('profit_mean_pct', 0.0),
            'total_profit_pct': pair_data.get('profit_total_pct', 0.0),
            'total_profit_abs': pair_data.get('profit_total_abs', 0.0),
            'win_rate': pair_data.get('wins', 0) / max(pair_data.get('trades', 1), 1) * 100,
            'max_drawdown': pair_data.get('max_drawdown_abs', 0.0),
            'profit_factor': pair_data.get('profit_factor', 0.0),
            'expectancy': pair_data.get('expectancy', 0.0)
        }
        
    except Exception as e:
        print(f"❌ 解析{pair}的ZIP文件失败: {e}")
        return {'pair': pair, 'total_trades': 0, 'total_profit_pct': 0.0}

def parse_backtest_json(json_file_path, pair):
    """从JSON文件解析回测结果"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strategy_data = data.get('strategy', {})
        if not strategy_data:
            return {'pair': pair, 'total_trades': 0, 'total_profit_pct': 0.0}
        
        # 查找对应代币的数据，或使用TOTAL数据
        pair_data = None
        for key, value in strategy_data.items():
            if isinstance(value, dict) and ('results_per_pair' in value or 'results_per_enter_tag' in value):
                results_per_pair = value.get('results_per_pair', [])
                # 寻找具体代币的数据
                for result in results_per_pair:
                    if result.get('key') == pair:
                        pair_data = result
                        break
                
                # 如果没找到具体代币，使用TOTAL数据
                if not pair_data:
                    for result in results_per_pair:
                        if result.get('key') == 'TOTAL':
                            pair_data = result
                            break
                
                if pair_data:
                    break
        
        if not pair_data:
            return {'pair': pair, 'total_trades': 0, 'total_profit_pct': 0.0}
        
        return {
            'pair': pair,
            'total_trades': pair_data.get('trades', 0),
            'avg_profit_pct': pair_data.get('profit_mean_pct', 0.0),
            'total_profit_pct': pair_data.get('profit_total_pct', 0.0),
            'total_profit_abs': pair_data.get('profit_total_abs', 0.0),
            'win_rate': pair_data.get('wins', 0) / max(pair_data.get('trades', 1), 1) * 100,
            'max_drawdown': pair_data.get('max_drawdown_abs', 0.0),
            'profit_factor': pair_data.get('profit_factor', 0.0),
            'expectancy': pair_data.get('expectancy', 0.0)
        }
        
    except Exception as e:
        print(f"❌ 解析{pair}的JSON文件失败: {e}")
        return {'pair': pair, 'total_trades': 0, 'total_profit_pct': 0.0}

def parse_backtest_result(output, pair):
    """解析回测结果"""
    lines = output.split('\n')
    result = {'pair': pair}
    
    # 查找表格中的结果
    in_main_table = False
    for line in lines:
        # 检查是否是主要的回测结果表格
        if '│ TOTAL │' in line and 'USDT' in line:
            # 解析TOTAL行的数据
            parts = [p.strip() for p in line.split('│') if p.strip()]
            if len(parts) >= 5:
                try:
                    result['total_trades'] = int(parts[1]) if parts[1].isdigit() else 0
                    result['avg_profit_pct'] = float(parts[2]) if parts[2] != '-' else 0.0
                    result['total_profit_usdt'] = float(parts[3]) if parts[3] != '-' else 0.0
                    result['total_profit_pct'] = float(parts[4]) if parts[4] != '-' else 0.0
                except (ValueError, IndexError):
                    pass
        
        # 提取其他重要指标
        elif '│ Total profit %' in line:
            match = re.search(r'│\s*Total profit %\s*│\s*([+-]?\d+\.?\d*)%', line)
            if match:
                result['total_profit_pct'] = float(match.group(1))
        
        elif '│ Sharpe' in line:
            match = re.search(r'│\s*Sharpe\s*│\s*([+-]?\d+\.?\d*)', line)
            if match:
                result['sharpe'] = float(match.group(1))
        
        elif '│ Profit factor' in line:
            match = re.search(r'│\s*Profit factor\s*│\s*([+-]?\d+\.?\d*)', line)
            if match:
                result['profit_factor'] = float(match.group(1))
        
        elif '│ Max % of account underwater' in line:
            match = re.search(r'│\s*Max % of account underwater\s*│\s*([+-]?\d+\.?\d*)%', line)
            if match:
                result['max_drawdown'] = float(match.group(1))
        
        elif '│ CAGR %' in line:
            match = re.search(r'│\s*CAGR %\s*│\s*([+-]?\d+\.?\d*)%', line)
            if match:
                result['cagr'] = float(match.group(1))
    
    # 设置默认值
    if 'total_trades' not in result:
        result['total_trades'] = 0
    if 'total_profit_pct' not in result:
        result['total_profit_pct'] = 0.0
    if 'total_profit_usdt' not in result:
        result['total_profit_usdt'] = 0.0
    
    return result

def classify_performance(results):
    """根据表现分类代币"""
    # 按总利润排序
    sorted_results = sorted(results, key=lambda x: x.get('total_profit_pct', -999), reverse=True)
    
    total_count = len(sorted_results)
    good_count = int(total_count * 0.3)  # 前30%为好
    bad_count = int(total_count * 0.3)   # 后30%为差
    
    good_performers = sorted_results[:good_count]
    bad_performers = sorted_results[-bad_count:]
    average_performers = sorted_results[good_count:-bad_count] if bad_count > 0 else sorted_results[good_count:]
    
    return {
        'good': good_performers,
        'average': average_performers,
        'bad': bad_performers
    }

def save_results(classified_results, output_file):
    """保存分类结果"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classified_results, f, indent=2, ensure_ascii=False)
    
    # 同时创建CSV格式的汇总
    all_results = []
    for category, results in classified_results.items():
        for result in results:
            result['category'] = category
            all_results.append(result)
    
    df = pd.DataFrame(all_results)
    csv_file = output_file.replace('.json', '.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    return csv_file

def write_markdown_results(results, failed_pairs, output_file):
    """将结果写入Markdown文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 批量回测结果报告\n\n")
        f.write(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**策略**: UniversalMACD1m\n")
        f.write(f"**时间框架**: 1m\n\n")
        
        f.write("## 📊 汇总统计\n\n")
        f.write(f"- 总测试代币: {len(results) + len(failed_pairs)}\n")
        f.write(f"- 成功测试: {len(results)}\n")
        f.write(f"- 失败测试: {len(failed_pairs)}\n\n")
        
        if results:
            # 按利润排序
            sorted_results = sorted(results, key=lambda x: x.get('total_profit_pct', -999), reverse=True)
            
            # 分类统计
            profitable = [r for r in sorted_results if r.get('total_profit_pct', 0) > 0]
            breakeven = [r for r in sorted_results if r.get('total_profit_pct', 0) == 0]
            losing = [r for r in sorted_results if r.get('total_profit_pct', 0) < 0]
            
            f.write(f"- 盈利代币: {len(profitable)} ({len(profitable)/len(results)*100:.1f}%)\n")
            f.write(f"- 盈亏平衡: {len(breakeven)} ({len(breakeven)/len(results)*100:.1f}%)\n")
            f.write(f"- 亏损代币: {len(losing)} ({len(losing)/len(results)*100:.1f}%)\n\n")
            
            f.write("## 🏆 表现最好的代币 (前20名)\n\n")
            f.write("| 排名 | 代币 | 总利润% | 交易次数 | 胜率% | 平均利润% |\n")
            f.write("|------|------|---------|----------|-------|----------|\n")
            
            for i, result in enumerate(sorted_results[:20], 1):
                pair = result.get('pair', '')
                total_profit = result.get('total_profit_pct', 0)
                trades = result.get('total_trades', 0)
                win_rate = result.get('win_rate', 0)
                avg_profit = result.get('avg_profit_pct', 0)
                f.write(f"| {i} | {pair} | {total_profit:.2f}% | {trades} | {win_rate:.1f}% | {avg_profit:.2f}% |\n")
            
            f.write("\n## 📉 表现最差的代币 (后20名)\n\n")
            f.write("| 排名 | 代币 | 总利润% | 交易次数 | 胜率% | 平均利润% |\n")
            f.write("|------|------|---------|----------|-------|----------|\n")
            
            for i, result in enumerate(sorted_results[-20:], len(sorted_results)-19):
                pair = result.get('pair', '')
                total_profit = result.get('total_profit_pct', 0)
                trades = result.get('total_trades', 0)
                win_rate = result.get('win_rate', 0)
                avg_profit = result.get('avg_profit_pct', 0)
                f.write(f"| {i} | {pair} | {total_profit:.2f}% | {trades} | {win_rate:.1f}% | {avg_profit:.2f}% |\n")
            
            f.write("\n## 📋 完整结果列表\n\n")
            f.write("| 代币 | 总利润% | 交易次数 | 胜率% | 平均利润% | 盈利因子 | 期望值 |\n")
            f.write("|------|---------|----------|-------|----------|----------|--------|\n")
            
            for result in sorted_results:
                pair = result.get('pair', '')
                total_profit = result.get('total_profit_pct', 0)
                trades = result.get('total_trades', 0)
                win_rate = result.get('win_rate', 0)
                avg_profit = result.get('avg_profit_pct', 0)
                profit_factor = result.get('profit_factor', 0)
                expectancy = result.get('expectancy', 0)
                f.write(f"| {pair} | {total_profit:.2f}% | {trades} | {win_rate:.1f}% | {avg_profit:.2f}% | {profit_factor:.2f} | {expectancy:.2f} |\n")
        
        if failed_pairs:
            f.write("\n## ❌ 失败的代币\n\n")
            for pair in failed_pairs:
                f.write(f"- {pair}\n")

def main():
    # 配置参数
    config_path = 'user_data/config_alpha.json'
    strategy = 'UniversalMACD5m'
    fee = 0.001
    timeframe = '5m'
    
    # 创建输出目录
    output_dir = 'batch_backtest_results'
    os.makedirs(output_dir, exist_ok=True)
    
    # 确定进程数（使用CPU核心数，但不超过6个避免过载）
    num_processes = min(cpu_count(), 8)
    
    print("🚀 开始多进程批量单币种回测...")
    print(f"🔧 使用 {num_processes} 个并行进程")
    print(f"📁 结果保存到: {output_dir}")
    print(f"⏱️  每个代币最多 30 秒")
    
    # 加载代币列表
    pairs = load_pairs_from_config(config_path)
    print(f"📋 找到 {len(pairs)} 个代币待测试")
    
    # 创建共享进度跟踪
    manager = Manager()
    progress_dict = manager.dict()
    progress_dict['completed'] = 0
    progress_dict['total'] = len(pairs)
    progress_dict['lock'] = manager.Lock()
    
    # 准备配置数据
    config_data = (config_path, strategy, fee, timeframe, output_dir, progress_dict)
    
    # 创建偏函数，固定配置参数
    backtest_func = partial(run_single_pair_backtest, config_data)
    
    # 并行运行回测
    start_time = time.time()
    print(f"⏳ 开始并行回测...")
    
    with Pool(processes=num_processes) as pool:
        all_results = pool.map(backtest_func, pairs)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 分离成功和失败的结果
    results = []
    failed_pairs = []
    
    for result in all_results:
        if result and result.get('status') in ['success', None] and result.get('total_trades', 0) >= 0:
            results.append(result)
        else:
            failed_pairs.append(result)
    
    print(f"\n🎉 多进程回测完成! 用时: {duration/60:.1f} 分钟")
    print(f"✅ 成功: {len(results)} 个")
    print(f"❌ 失败: {len(failed_pairs)} 个")
    print(f"⚡ 平均速度: {len(pairs)/duration:.1f} 代币/秒")
    
    if results:
        # 生成Markdown报告
        markdown_file = f'{output_dir}/batch_backtest_report_{int(time.time())}.md'
        write_markdown_results(results, failed_pairs, markdown_file)
        
        # 按利润排序显示快速预览
        sorted_results = sorted(results, key=lambda x: x.get('total_profit_pct', -999), reverse=True)
        
        print(f"\n📈 表现最好的5个:")
        for r in sorted_results[:5]:
            print(f"   {r['pair']}: {r.get('total_profit_pct', 0):.2f}% ({r.get('total_trades', 0)} 笔交易)")
        
        print(f"\n📉 表现最差的5个:")
        for r in sorted_results[-5:]:
            print(f"   {r['pair']}: {r.get('total_profit_pct', 0):.2f}% ({r.get('total_trades', 0)} 笔交易)")
        
        # 分类统计
        profitable = [r for r in results if r.get('total_profit_pct', 0) > 0]
        losing = [r for r in results if r.get('total_profit_pct', 0) < 0]
        breakeven = [r for r in results if r.get('total_profit_pct', 0) == 0]
        
        print(f"\n📊 分类统计:")
        print(f"🟢 盈利代币: {len(profitable)} ({len(profitable)/len(results)*100:.1f}%)")
        print(f"🟡 盈亏平衡: {len(breakeven)} ({len(breakeven)/len(results)*100:.1f}%)")
        print(f"🔴 亏损代币: {len(losing)} ({len(losing)/len(results)*100:.1f}%)")
        
        print(f"\n💾 详细结果已保存到: {markdown_file}")
        print(f"📖 请打开该文件查看完整的分析报告")

if __name__ == "__main__":
    main()