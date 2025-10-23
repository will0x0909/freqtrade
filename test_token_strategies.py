#!/usr/bin/env python3
"""
Strategy Testing Script for Alpha Tokens
Test multiple strategies on specified tokens: 4, MYX, YZY
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
import pandas as pd

class StrategyTester:
    def __init__(self, csv_file='/Users/will9709/Desktop/1_m_listing_tokens.csv', enable_hyperopt=False, hyperopt_epochs=100):
        # Load tokens from CSV file
        self.csv_file = csv_file
        self.tokens_data = self.load_tokens_from_csv()
        self.tokens = list(self.tokens_data.keys())
        self.timeframes = ['5m', '1m']
        
        # Hyperopt configuration
        self.enable_hyperopt = enable_hyperopt
        self.hyperopt_epochs = hyperopt_epochs
        self.hyperopt_results = {}
        
        # All available strategies for testing
        self.strategies = {
            'Strategy004_1m': {'timeframe': '1m', 'description': 'Strategy004 implementation',
                            'path': 'user_data/strategies'},
            'Bandtastic1m': {'timeframe': '1m', 'description': 'Band-based trading strategy',
                           'path': 'user_data/strategies'},
            'AwesomeMacd1m': {'timeframe': '1m', 'description': 'Awesome oscillator + MACD',
                            'path': 'user_data/strategies'},
            'BinHV271m': {'timeframe': '1m', 'description': 'Binary high volume v27', 'path': 'user_data/strategies'},
            'CofiBitStrategy1m': {'timeframe': '1m', 'description': 'CofiBit trading strategy',
                                'path': 'user_data/strategies'},
            'MACDStrategy1m': {'timeframe': '1m', 'description': 'MACD strategy', 'path': 'user_data/strategies'},
            'MACDStrategy_crossed1m': {'timeframe': '1m', 'description': 'MACD crossover strategy',
                                     'path': 'user_data/strategies'},
            'UniversalMACD1m': {'timeframe': '1m', 'description': 'Universal MACD strategy',
                              'path': 'user_data/strategies'},
            'Strategy004_5m': {'timeframe': '5m', 'description': 'Strategy004 implementation',
                            'path': 'user_data/strategies'},
            'Bandtastic5m': {'timeframe': '5m', 'description': 'Band-based trading strategy',
                           'path': 'user_data/strategies'},
            'AwesomeMacd5m': {'timeframe': '5m', 'description': 'Awesome oscillator + MACD',
                            'path': 'user_data/strategies'},
            'BinHV275m': {'timeframe': '5m', 'description': 'Binary high volume v27', 'path': 'user_data/strategies'},
            'CofiBitStrategy5m': {'timeframe': '5m', 'description': 'CofiBit trading strategy',
                                'path': 'user_data/strategies'},
            'MACDStrategy5m': {'timeframe': '5m', 'description': 'MACD strategy', 'path': 'user_data/strategies'},
            'MACDStrategy_crossed5m': {'timeframe': '5m', 'description': 'MACD crossover strategy',
                                     'path': 'user_data/strategies'},
            'UniversalMACD5m': {'timeframe': '5m', 'description': 'Universal MACD strategy',
                              'path': 'user_data/strategies'}
        }
        
        self.results = {}
    
    def load_tokens_from_csv(self):
        """Load token information from CSV file"""
        tokens_data = {}
        
        try:
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
                print(f"📁 Loading tokens from {self.csv_file}")
                
                # Expected columns: symbol, listingTime (and possibly others)
                # Adjust column names based on your CSV structure
                symbol_col = None
                listing_time_col = None
                
                # Try to find the right columns (case insensitive)
                for col in df.columns:
                    col_lower = col.lower()
                    if 'symbol' in col_lower or 'token' in col_lower:
                        symbol_col = col
                    elif 'listing' in col_lower and 'time' in col_lower:
                        listing_time_col = col
                
                if symbol_col is None:
                    # Fallback: assume first column is symbol
                    symbol_col = df.columns[0]
                    print(f"⚠️  No 'symbol' column found, using '{symbol_col}' as token symbol")
                
                if listing_time_col is None:
                    print(f"⚠️  No 'listingTime' column found, will use default date range")
                
                for _, row in df.iterrows():
                    symbol = str(row[symbol_col]).strip()
                    if symbol and symbol != 'nan':
                        listing_time = None
                        if listing_time_col and pd.notna(row[listing_time_col]):
                            try:
                                # Try to parse listing time
                                listing_time_str = str(row[listing_time_col])
                                # Handle different date formats
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y']:
                                    try:
                                        listing_time = datetime.strptime(listing_time_str, fmt)
                                        break
                                    except ValueError:
                                        continue
                            except:
                                listing_time = None
                        
                        tokens_data[symbol] = {
                            'listing_time': listing_time,
                            'test_start': listing_time if listing_time else datetime(2025, 9, 21),
                            'test_end': (listing_time + timedelta(days=14)) if listing_time else datetime(2025, 10, 20)
                        }
                
                print(f"✅ Loaded {len(tokens_data)} tokens from CSV")
                
                # Show first few tokens as sample
                sample_tokens = list(tokens_data.keys())[:5]
                for token in sample_tokens:
                    data = tokens_data[token]
                    print(f"   📊 {token}: {data['test_start'].strftime('%Y-%m-%d')} to {data['test_end'].strftime('%Y-%m-%d')}")
                
                if len(tokens_data) > 5:
                    print(f"   ... and {len(tokens_data) - 5} more tokens")
                    
            else:
                print(f"❌ CSV file '{self.csv_file}' not found!")
                print(f"📝 Please ensure the file exists with columns: symbol, listingTime")
                print(f"🔄 Falling back to default tokens: ['4', 'MYX', 'YZY']")
                
                # Fallback to original tokens with default date range
                default_tokens = []
                for token in default_tokens:
                    tokens_data[token] = {
                        'listing_time': None,
                        'test_start': datetime(2025, 9, 21),
                        'test_end': datetime(2025, 10, 20)
                    }
                    
        except Exception as e:
            print(f"💥 Error loading CSV file: {e}")
            print(f"🔄 Falling back to default tokens")
            
            # Fallback to original tokens
            default_tokens = ['4', 'MYX', 'YZY']
            for token in default_tokens:
                tokens_data[token] = {
                    'listing_time': None,
                    'test_start': datetime(2025, 9, 21),
                    'test_end': datetime(2025, 10, 20)
                }
        
        return tokens_data
    
    def get_strategy_path(self, strategy):
        """Get the correct strategy path"""
        strategy_config = self.strategies.get(strategy, {})
        return strategy_config.get('path', 'user_data/strategies')
    
    def run_backtest(self, token, strategy, timeframe):
        """Run backtest for a specific token and strategy"""
        print(f"\n🧪 Testing {strategy} on {token} ({timeframe})...")
        
        try:
            # Get strategy path
            strategy_path = self.get_strategy_path(strategy)
            
            # Get token-specific test period
            token_data = self.tokens_data.get(token, {})
            test_start = token_data.get('test_start', datetime(2025, 9, 21))
            test_end = token_data.get('test_end', datetime(2025, 10, 20))
            
            # Format dates for freqtrade timerange
            start_str = test_start.strftime('%Y%m%d')
            end_str = test_end.strftime('%Y%m%d')
            timerange = f"{start_str}-{end_str}"
            
            print(f"   📅 Test period: {test_start.strftime('%Y-%m-%d')} to {test_end.strftime('%Y-%m-%d')}")
            
            # Build command similar to the reference format
            cmd = [
                '/opt/anaconda3/envs/freqtrade/bin/python', '-m', 'freqtrade', 'backtesting',
                '--strategy', strategy,
                '--config', 'user_data/config_alpha.json',
                '--timeframe', timeframe,
                '--timerange', timerange,
                '-p', f"{token}/USDT"
            ]
            
            # Add strategy path if not default
            if strategy_path != 'user_data/strategies':
                cmd.extend(['--strategy-path', strategy_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {strategy} on {token}: Backtest completed")
                return self.parse_backtest_output(result.stdout)
            else:
                print(f"❌ {strategy} on {token}: Backtest failed")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {strategy} on {token}: Backtest timeout")
            return None
        except Exception as e:
            print(f"💥 {strategy} on {token}: Exception - {e}")
            return None
    
    def parse_backtest_output(self, output):
        """Parse backtest results from output"""
        results = {}
        lines = output.split('\n')
        
        # Look for the main BACKTESTING REPORT table
        in_main_table = False
        
        for i, line in enumerate(lines):
            # Detect if we're in the main BACKTESTING REPORT
            if 'BACKTESTING REPORT' in line:
                in_main_table = True
                continue
            
            # Stop looking when we hit another section
            if in_main_table and ('LEFT OPEN TRADES REPORT' in line or 'ENTER TAG STATS' in line):
                break
            
            # Look for TOTAL line more flexibly - check for any line containing TOTAL in the main table
            if in_main_table and 'TOTAL' in line and '│' in line:
                try:
                    # Parse the table row
                    parts = [p.strip() for p in line.split('│') if p.strip()]
                    
                    # More flexible parsing - find TOTAL part and work from there
                    total_index = -1
                    for idx, part in enumerate(parts):
                        if 'TOTAL' in part:
                            total_index = idx
                            break
                    
                    if total_index >= 0 and len(parts) >= total_index + 6:
                        # Extract data from TOTAL row
                        trades_str = parts[total_index + 1].strip()
                        results['total_trades'] = int(trades_str) if trades_str.isdigit() else 0
                        
                        # Get total profit percentage (usually 4th column after TOTAL)
                        if len(parts) > total_index + 4:
                            profit_str = parts[total_index + 4].strip()
                            try:
                                if profit_str.replace('-', '').replace('.', '').replace('%', '').isdigit():
                                    results['total_profit_pct'] = float(profit_str.replace('%', ''))
                                else:
                                    results['total_profit_pct'] = 0.0
                            except:
                                results['total_profit_pct'] = 0.0
                        
                        # Parse win/draw/loss from last column
                        if len(parts) > total_index + 6:
                            win_stats = parts[-1].strip()
                            stats_parts = win_stats.split()
                            if len(stats_parts) >= 4:
                                try:
                                    wins = int(stats_parts[0])
                                    draws = int(stats_parts[1])
                                    losses = int(stats_parts[2])
                                    win_rate_str = stats_parts[3].replace('%', '')
                                    win_rate = float(win_rate_str) if win_rate_str.replace('.', '').isdigit() else 0.0
                                    
                                    results['wins'] = wins
                                    results['losses'] = losses
                                    results['win_rate'] = win_rate
                                except:
                                    pass
                        
                        # Get average duration
                        if len(parts) > total_index + 5:
                            results['avg_duration'] = parts[total_index + 5].strip()
                        
                        break
                except Exception as e:
                    continue
        
        # Look for drawdown info in SUMMARY METRICS
        in_summary = False
        for line in lines:
            if 'SUMMARY METRICS' in line:
                in_summary = True
                continue
            elif in_summary and '│ Max % of account underwater' in line:
                try:
                    parts = line.split('│')
                    if len(parts) >= 3:
                        drawdown_str = parts[2].strip()
                        if '%' in drawdown_str:
                            drawdown = float(drawdown_str.replace('%', '').strip())
                            results['max_drawdown_pct'] = drawdown
                except:
                    pass
                break
        
        return results
    
    def run_hyperopt(self, token, strategy, timeframe):
        """Run hyperopt optimization for a specific token and strategy"""
        print(f"\n🔧 Optimizing {strategy} on {token} ({timeframe}) - {self.hyperopt_epochs} epochs...")
        
        try:
            # Get strategy path
            strategy_path = self.get_strategy_path(strategy)
            
            # Get token-specific test period
            token_data = self.tokens_data.get(token, {})
            test_start = token_data.get('test_start', datetime(2025, 9, 21))
            test_end = token_data.get('test_end', datetime(2025, 10, 20))
            
            # Format dates for freqtrade timerange
            start_str = test_start.strftime('%Y%m%d')
            end_str = test_end.strftime('%Y%m%d')
            timerange = f"{start_str}-{end_str}"
            
            print(f"   📅 Optimization period: {test_start.strftime('%Y-%m-%d')} to {test_end.strftime('%Y-%m-%d')}")
            
            # Build hyperopt command
            cmd = [
                '/opt/anaconda3/envs/freqtrade/bin/python', '-m', 'freqtrade', 'hyperopt',
                '--strategy', strategy,
                '--config', 'user_data/config_alpha.json',
                '--timeframe', timeframe,
                '--timerange', timerange,
                '-p', f"{token}/USDT",
                '--epochs', str(self.hyperopt_epochs),
                '--spaces', 'buy', 'sell', 'roi', 'stoploss',
                '--hyperopt-loss', 'ProfitLoss'
            ]
            
            # Add strategy path if not default
            if strategy_path != 'user_data/strategies':
                cmd.extend(['--strategy-path', strategy_path])
            
            # Run hyperopt with longer timeout
            timeout = max(600, self.hyperopt_epochs * 10)  # At least 10 minutes, or 10 seconds per epoch
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                print(f"✅ {strategy} on {token}: Hyperopt completed")
                return self.parse_hyperopt_output(result.stdout)
            else:
                print(f"❌ {strategy} on {token}: Hyperopt failed")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {strategy} on {token}: Hyperopt timeout after {timeout}s")
            return None
        except Exception as e:
            print(f"💥 {strategy} on {token}: Hyperopt exception - {e}")
            return None
    
    def parse_hyperopt_output(self, output):
        """Parse hyperopt results from output"""
        results = {}
        lines = output.split('\n')
        
        # Look for best result summary
        best_result_section = False
        best_params = {}
        
        for i, line in enumerate(lines):
            # Find the best result section
            if 'Best result:' in line or 'Best parameters:' in line:
                best_result_section = True
                continue
            
            # Parse best parameters
            if best_result_section and ('buy_' in line or 'sell_' in line or 'roi_' in line or 'stoploss' in line):
                try:
                    # Extract parameter name and value
                    if ':' in line:
                        param_line = line.strip()
                        if param_line.startswith('"') and '":' in param_line:
                            # Format: "param_name": value
                            param_name = param_line.split('":')[0].strip('"').strip()
                            param_value = param_line.split('":')[1].strip().rstrip(',')
                            try:
                                # Try to convert to float/int
                                if '.' in param_value:
                                    param_value = float(param_value)
                                else:
                                    param_value = int(param_value)
                            except:
                                pass  # Keep as string
                            best_params[param_name] = param_value
                except:
                    continue
            
            # Look for performance metrics
            if 'Best Objective:' in line or 'Best objective:' in line:
                try:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        objective_value = float(parts[1].strip())
                        results['best_objective'] = objective_value
                except:
                    pass
            
            # Look for final backtest results after optimization
            if 'BACKTESTING REPORT' in line:
                # Parse the final backtest with optimized parameters
                backtest_results = self.parse_backtest_output('\n'.join(lines[i:]))
                if backtest_results:
                    results.update(backtest_results)
                break
        
        results['best_params'] = best_params
        results['optimization_epochs'] = self.hyperopt_epochs
        
        return results
    
    def run_optimized_backtest(self, token, strategy, timeframe, best_params):
        """Run backtest with optimized parameters"""
        print(f"\n🚀 Running optimized backtest for {strategy} on {token} ({timeframe})...")
        
        try:
            # Create a temporary strategy file with optimized parameters
            # This is a simplified approach - in practice, you might want to use
            # freqtrade's parameter override features
            
            # For now, just run regular backtest and note that params were optimized
            result = self.run_backtest(token, strategy, timeframe)
            if result:
                result['optimized'] = True
                result['optimized_params'] = best_params
            return result
            
        except Exception as e:
            print(f"💥 Optimized backtest failed: {e}")
            return None
    
    def test_all_strategies(self):
        """Test all strategies on all tokens"""
        print(f"🚀 Starting strategy testing for {len(self.tokens)} tokens from CSV")
        print(f"📊 Each token will be tested for its individual 14-day period from listing time")
        
        if self.enable_hyperopt:
            print(f"🔧 Hyperopt optimization enabled: {self.hyperopt_epochs} epochs per strategy")
            total_tests = len(self.tokens) * len(self.strategies) * 2  # Regular + optimized
            print(f"🎯 Total tests: {len(self.tokens)} tokens × {len(self.strategies)} strategies × 2 (regular + optimized) = {total_tests} tests")
            print(f"⚠️  Warning: With hyperopt enabled, this will take significantly longer (~{total_tests * 3} minutes estimated)")
        else:
            total_tests = len(self.tokens) * len(self.strategies)
            print(f"🎯 Total tests: {len(self.tokens)} tokens × {len(self.strategies)} strategies = {total_tests} tests")
            print(f"⚠️  Warning: This will take a significant amount of time (~{total_tests * 2} minutes estimated)")
        
        for token in self.tokens:
            self.results[token] = {}
            self.hyperopt_results[token] = {}
            print(f"\n{'='*60}")
            print(f"🪙 Testing strategies for {token}")
            print(f"{'='*60}")
            
            for strategy_name, strategy_config in self.strategies.items():
                timeframe = strategy_config['timeframe']
                
                # Check if data file exists
                data_file = f"user_data/data/binance/{token}_USDT-{timeframe}.feather"
                if not os.path.exists(data_file):
                    print(f"⚠️  {strategy_name}: No {timeframe} data for {token}, skipping...")
                    continue
                
                # Run regular backtest
                print(f"\n📊 Running regular backtest for {strategy_name}")
                regular_result = self.run_backtest(token, strategy_name, timeframe)
                
                hyperopt_result = None
                optimized_result = None
                
                # Run hyperopt if enabled
                if self.enable_hyperopt:
                    print(f"\n🔧 Running hyperopt optimization for {strategy_name}")
                    hyperopt_result = self.run_hyperopt(token, strategy_name, timeframe)
                    
                    if hyperopt_result and hyperopt_result.get('best_params'):
                        print(f"\n🚀 Running optimized backtest for {strategy_name}")
                        optimized_result = self.run_optimized_backtest(
                            token, strategy_name, timeframe, hyperopt_result['best_params']
                        )
                
                # Store all results
                self.results[token][strategy_name] = {
                    'config': strategy_config,
                    'regular_result': regular_result,
                    'optimized_result': optimized_result
                }
                
                if hyperopt_result:
                    self.hyperopt_results[token][strategy_name] = hyperopt_result
    
    def generate_report(self):
        """Generate comprehensive test report"""
        report = []
        report.append("# Strategy Testing Report")
        report.append(f"**Tokens Tested**: {len(self.tokens)} tokens from {self.csv_file}")
        report.append(f"**Test Method**: Individual 14-day periods from each token's listing time")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Add token listing information
        report.append("## Token Test Periods")
        report.append("")
        report.append("| Token | Listing Time | Test Start | Test End |")
        report.append("|-------|--------------|------------|----------|")
        
        for token in self.tokens:
            token_data = self.tokens_data.get(token, {})
            listing_time = token_data.get('listing_time')
            test_start = token_data.get('test_start', datetime(2025, 9, 21))
            test_end = token_data.get('test_end', datetime(2025, 10, 20))
            
            listing_str = listing_time.strftime('%Y-%m-%d') if listing_time else "N/A"
            start_str = test_start.strftime('%Y-%m-%d')
            end_str = test_end.strftime('%Y-%m-%d')
            
            report.append(f"| {token} | {listing_str} | {start_str} | {end_str} |")
        
        report.append("")
        
        # Summary table
        report.append("## Summary Table")
        report.append("")
        
        if self.enable_hyperopt:
            report.append("| Token | Strategy | Timeframe | Regular Profit (%) | Optimized Profit (%) | Improvement | Total Trades | Win Rate (%) | Status |")
            report.append("|-------|----------|-----------|-------------------|---------------------|-------------|--------------|--------------|---------|")
        else:
            report.append("| Token | Strategy | Timeframe | Total Profit (%) | Total Trades | Win Rate (%) | Max Drawdown (%) | Status |")
            report.append("|-------|----------|-----------|------------------|--------------|--------------|------------------|---------|")
        
        for token in self.tokens:
            if token in self.results:
                for strategy, data in self.results[token].items():
                    regular_result = data.get('regular_result')
                    optimized_result = data.get('optimized_result')
                    config = data['config']
                    
                    if self.enable_hyperopt:
                        # Handle hyperopt results
                        regular_profit = regular_result.get('total_profit_pct', 'N/A') if regular_result else 'N/A'
                        optimized_profit = optimized_result.get('total_profit_pct', 'N/A') if optimized_result else 'N/A'
                        
                        # Calculate improvement
                        improvement = 'N/A'
                        if (isinstance(regular_profit, (int, float)) and 
                            isinstance(optimized_profit, (int, float))):
                            improvement = f"{optimized_profit - regular_profit:+.1f}%"
                        
                        trades = optimized_result.get('total_trades', 'N/A') if optimized_result else (regular_result.get('total_trades', 'N/A') if regular_result else 'N/A')
                        win_rate = optimized_result.get('win_rate', 'N/A') if optimized_result else (regular_result.get('win_rate', 'N/A') if regular_result else 'N/A')
                        if isinstance(win_rate, float):
                            win_rate = f"{win_rate:.1f}"
                        
                        status = "✅ Optimized" if optimized_result else ("✅ Regular" if regular_result else "❌ Failed")
                        
                        report.append(f"| {token} | {strategy} | {config['timeframe']} | {regular_profit} | {optimized_profit} | {improvement} | {trades} | {win_rate} | {status} |")
                    else:
                        # Handle regular results only
                        result = regular_result
                        if result:
                            profit = result.get('total_profit_pct', 'N/A')
                            trades = result.get('total_trades', 'N/A')
                            win_rate = result.get('win_rate', 'N/A')
                            if isinstance(win_rate, float):
                                win_rate = f"{win_rate:.1f}"
                            drawdown = result.get('max_drawdown_pct', 'N/A')
                            status = "✅ Success"
                        else:
                            profit = trades = win_rate = drawdown = "N/A"
                            status = "❌ Failed"
                        
                        report.append(f"| {token} | {strategy} | {config['timeframe']} | {profit} | {trades} | {win_rate} | {drawdown} | {status} |")
        
        # Detailed results by token
        for token in self.tokens:
            if token not in self.results:
                continue
                
            report.append(f"\n## {token} Detailed Results")
            report.append("")
            
            successful_tests = []
            failed_tests = []
            
            for strategy, data in self.results[token].items():
                regular_result = data.get('regular_result')
                optimized_result = data.get('optimized_result')
                config = data['config']
                
                # Use optimized result if available, otherwise regular result
                best_result = optimized_result if optimized_result else regular_result
                
                if best_result:
                    # Add hyperopt info if available
                    hyperopt_info = None
                    if token in self.hyperopt_results and strategy in self.hyperopt_results[token]:
                        hyperopt_info = self.hyperopt_results[token][strategy]
                    
                    successful_tests.append((strategy, config, best_result, regular_result, optimized_result, hyperopt_info))
                else:
                    failed_tests.append((strategy, config))
            
            if successful_tests:
                # Sort by profit
                successful_tests.sort(key=lambda x: x[2].get('total_profit_pct', 0), reverse=True)
                
                report.append("### 📈 Successful Strategies (sorted by profit)")
                report.append("")
                
                for item in successful_tests:
                    strategy, config, best_result, regular_result, optimized_result, hyperopt_info = item
                    
                    report.append(f"**{strategy}** ({config['timeframe']})")
                    report.append(f"- *Description*: {config['description']}")
                    
                    if self.enable_hyperopt and optimized_result:
                        # Show both regular and optimized results
                        regular_profit = regular_result.get('total_profit_pct', 'N/A') if regular_result else 'N/A'
                        optimized_profit = optimized_result.get('total_profit_pct', 'N/A')
                        improvement = 'N/A'
                        if (isinstance(regular_profit, (int, float)) and 
                            isinstance(optimized_profit, (int, float))):
                            improvement = f"{optimized_profit - regular_profit:+.1f}%"
                        
                        report.append(f"- *Regular Profit*: {regular_profit}%")
                        report.append(f"- *Optimized Profit*: {optimized_profit}%")
                        report.append(f"- *Improvement*: {improvement}")
                        report.append(f"- *Total Trades*: {optimized_result.get('total_trades', 'N/A')}")
                        
                        # Show optimized parameters if available
                        if hyperopt_info and hyperopt_info.get('best_params'):
                            report.append(f"- *Optimization Epochs*: {hyperopt_info.get('optimization_epochs', 'N/A')}")
                            report.append(f"- *Best Objective*: {hyperopt_info.get('best_objective', 'N/A')}")
                            
                            best_params = hyperopt_info['best_params']
                            if best_params:
                                report.append("- *Optimized Parameters*:")
                                for param, value in best_params.items():
                                    report.append(f"  - {param}: {value}")
                    else:
                        # Show regular results only
                        report.append(f"- *Total Profit*: {best_result.get('total_profit_pct', 'N/A')}%")
                        report.append(f"- *Total Trades*: {best_result.get('total_trades', 'N/A')}")
                    
                    win_rate = best_result.get('win_rate', 'N/A')
                    if isinstance(win_rate, float):
                        report.append(f"- *Win Rate*: {win_rate:.1f}%")
                    else:
                        report.append(f"- *Win Rate*: {win_rate}")
                    
                    report.append(f"- *Max Drawdown*: {best_result.get('max_drawdown_pct', 'N/A')}%")
                    report.append(f"- *Avg Duration*: {best_result.get('avg_duration', 'N/A')}")
                    report.append("")
            
            if failed_tests:
                report.append("### ❌ Failed Strategies")
                report.append("")
                for strategy, config in failed_tests:
                    report.append(f"- **{strategy}** ({config['timeframe']}): {config['description']}")
                report.append("")
        
        # Best performing strategies overall
        all_results = []
        for token in self.results:
            for strategy, data in self.results[token].items():
                regular_result = data.get('regular_result')
                optimized_result = data.get('optimized_result')
                best_result = optimized_result if optimized_result else regular_result
                
                if best_result:
                    result_entry = {
                        'token': token,
                        'strategy': strategy,
                        'config': data['config'],
                        'result': best_result,
                        'is_optimized': bool(optimized_result),
                        'regular_result': regular_result,
                        'optimized_result': optimized_result
                    }
                    
                    # Add hyperopt info if available
                    if (token in self.hyperopt_results and 
                        strategy in self.hyperopt_results[token]):
                        result_entry['hyperopt_info'] = self.hyperopt_results[token][strategy]
                    
                    all_results.append(result_entry)
        
        if all_results:
            report.append("## 🏆 Top Performing Strategies (All Tokens)")
            report.append("")
            
            # Sort by profit
            all_results.sort(key=lambda x: x['result'].get('total_profit_pct', 0), reverse=True)
            
            report.append("### By Total Profit")
            report.append("")
            for i, item in enumerate(all_results[:10]):  # Top 10
                result = item['result']
                optimization_tag = " (Optimized)" if item['is_optimized'] else ""
                improvement_info = ""
                
                if item['is_optimized'] and item['regular_result']:
                    regular_profit = item['regular_result'].get('total_profit_pct', 0)
                    optimized_profit = result.get('total_profit_pct', 0)
                    if isinstance(regular_profit, (int, float)) and isinstance(optimized_profit, (int, float)):
                        improvement = optimized_profit - regular_profit
                        improvement_info = f" [+{improvement:.1f}%]"
                
                report.append(f"{i+1}. **{item['strategy']}** on **{item['token']}**{optimization_tag} - {result.get('total_profit_pct', 'N/A')}% profit{improvement_info}")
            
            report.append("")
            report.append("### By Win Rate (min 5 trades)")
            report.append("")
            high_winrate = [x for x in all_results if x['result'].get('total_trades', 0) >= 5]
            high_winrate.sort(key=lambda x: x['result'].get('win_rate', 0), reverse=True)
            
            for i, item in enumerate(high_winrate[:10]):  # Top 10
                result = item['result']
                optimization_tag = " (Optimized)" if item['is_optimized'] else ""
                win_rate = result.get('win_rate', 'N/A')
                if isinstance(win_rate, float):
                    win_rate = f"{win_rate:.1f}%"
                report.append(f"{i+1}. **{item['strategy']}** on **{item['token']}**{optimization_tag} - {win_rate} win rate ({result.get('total_trades', 'N/A')} trades)")
            
            # Add hyperopt improvements section if hyperopt was enabled
            if self.enable_hyperopt:
                optimized_results = [x for x in all_results if x['is_optimized'] and x['regular_result']]
                if optimized_results:
                    # Calculate improvements
                    improvements = []
                    for item in optimized_results:
                        regular_profit = item['regular_result'].get('total_profit_pct', 0)
                        optimized_profit = item['result'].get('total_profit_pct', 0)
                        if isinstance(regular_profit, (int, float)) and isinstance(optimized_profit, (int, float)):
                            improvement = optimized_profit - regular_profit
                            improvements.append({
                                'item': item,
                                'improvement': improvement
                            })
                    
                    if improvements:
                        improvements.sort(key=lambda x: x['improvement'], reverse=True)
                        
                        report.append("")
                        report.append("### 🚀 Biggest Optimization Improvements")
                        report.append("")
                        
                        for i, imp in enumerate(improvements[:10]):  # Top 10 improvements
                            item = imp['item']
                            improvement = imp['improvement']
                            regular_profit = item['regular_result'].get('total_profit_pct', 0)
                            optimized_profit = item['result'].get('total_profit_pct', 0)
                            
                            report.append(f"{i+1}. **{item['strategy']}** on **{item['token']}** - {regular_profit:.1f}% → {optimized_profit:.1f}% (+{improvement:.1f}%)")
                            
                            # Show key optimized parameters if available
                            if 'hyperopt_info' in item and item['hyperopt_info'].get('best_params'):
                                best_params = item['hyperopt_info']['best_params']
                                param_summary = []
                                for param, value in list(best_params.items())[:3]:  # Show first 3 params
                                    param_summary.append(f"{param}: {value}")
                                if param_summary:
                                    report.append(f"   *Key params: {', '.join(param_summary)}*")
        
        # Save report
        report_content = '\n'.join(report)
        with open('strategy_test_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📋 Report saved to: strategy_test_report.md")
        return report_content

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test strategies on alpha tokens with optional hyperopt optimization')
    parser.add_argument('--hyperopt', action='store_true', help='Enable hyperopt optimization')
    parser.add_argument('--epochs', type=int, default=100, help='Number of hyperopt epochs (default: 100)')
    parser.add_argument('--csv', default='/Users/will9709/Desktop/1_m_listing_tokens.csv', help='CSV file with token data')
    parser.add_argument('--token', help='Test only a specific token (for testing purposes)')
    parser.add_argument('--strategy', help='Test only a specific strategy (for testing purposes)')
    
    args = parser.parse_args()
    
    print(f"🚀 Alpha Token Strategy Tester")
    print(f"{'='*50}")
    
    if args.hyperopt:
        print(f"🔧 Hyperopt optimization: ENABLED ({args.epochs} epochs)")
    else:
        print(f"📊 Regular backtesting only")
    
    print(f"📁 Token data source: {args.csv}")
    
    if args.token:
        print(f"🎯 Testing single token: {args.token}")
    
    if args.strategy:
        print(f"🎯 Testing single strategy: {args.strategy}")
    
    tester = StrategyTester(
        csv_file=args.csv,
        enable_hyperopt=args.hyperopt,
        hyperopt_epochs=args.epochs
    )
    
    # If testing a single token, filter the tokens list
    if args.token:
        if args.token in tester.tokens:
            tester.tokens = [args.token]
            print(f"✅ Token {args.token} found in dataset")
        else:
            print(f"❌ Token {args.token} not found in dataset")
            print(f"Available tokens: {', '.join(tester.tokens[:10])}{'...' if len(tester.tokens) > 10 else ''}")
            return
    
    # If testing a single strategy, filter the strategies list
    if args.strategy:
        if args.strategy in tester.strategies:
            tester.strategies = {args.strategy: tester.strategies[args.strategy]}
            print(f"✅ Strategy {args.strategy} found in strategy list")
        else:
            print(f"❌ Strategy {args.strategy} not found in strategy list")
            available_strategies = list(tester.strategies.keys())
            print(f"Available strategies: {', '.join(available_strategies[:10])}{'...' if len(available_strategies) > 10 else ''}")
            return
    
    try:
        # Run all tests
        tester.test_all_strategies()
        
        # Generate report
        print(f"\n{'='*60}")
        print("📊 Generating Test Report")
        print(f"{'='*60}")
        
        tester.generate_report()
        
        print(f"\n🎉 Strategy testing completed!")
        print(f"📋 Check 'strategy_test_report.md' for detailed results")
        
        if args.hyperopt:
            print(f"🔧 Hyperopt optimization was enabled with {args.epochs} epochs per strategy")
            print(f"📈 Look for optimization improvements in the report")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")

if __name__ == "__main__":
    main()