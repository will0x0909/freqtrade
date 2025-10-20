#!/usr/bin/env python3
"""
Script to fetch alpha token data from Binance API and convert to feather format.
Supports batch fetching by token_id from database.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import psycopg2
import pandas as pd


class AlphaDataFetcher:
    def __init__(self):
        self.base_url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/agg-klines"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Database connection for token lookup
        self.db_config = {
            'host': 'prod-01-instance-1.c9w68y62uzp5.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'database': 'crypto_price',
            'user': 'crypto_price', 
            'password': 'Vj8GNvqXmfHs'
        }

    def get_token_info(self, token_ids: List[int] = None) -> List[Dict]:
        """Get token information from database by token_id(s)"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            if token_ids:
                placeholders = ','.join(['%s'] * len(token_ids))
                query = f"""SELECT token_id, symbol, alpha_id, chain_id, contract_address 
                           FROM tokens 
                           WHERE token_id IN ({placeholders}) AND alpha_id IS NOT NULL
                           ORDER BY token_id"""
                cursor.execute(query, token_ids)
            else:
                cursor.execute("""SELECT token_id, symbol, alpha_id, chain_id, contract_address 
                                 FROM tokens 
                                 WHERE alpha_id IS NOT NULL 
                                 ORDER BY token_id""")
            
            tokens = []
            for row in cursor.fetchall():
                tokens.append({
                    'token_id': row[0],
                    'symbol': row[1],
                    'alpha_id': row[2],
                    'chain_id': row[3],
                    'contract_address': row[4]
                })
            
            conn.close()
            return tokens
        except Exception as e:
            print(f"Error fetching token info: {e}", file=sys.stderr)
            return []

    def get_alpha_symbols(self) -> List[str]:
        """Get all available alpha token symbols from database"""
        tokens = self.get_token_info()
        return [token['alpha_id'] + "USDT" for token in tokens]

    def fetch_data(self, 
                   token_info: Dict,
                   interval: str = "1h",
                   limit: int = 500,
                   start_time: Optional[int] = None,
                   end_time: Optional[int] = None) -> List[Dict]:
        """
        Fetch alpha token data from new Binance API
        
        Args:
            token_info: Token information dict with chain_id and contract_address
            interval: Time interval (1h, 1d, etc.)
            limit: Number of records to fetch
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        """
        params = {
            'chainId': token_info['chain_id'],
            'tokenAddress': token_info['contract_address'],
            'interval': interval,
            'limit': min(limit, 1000),  # API限制最大1000
            'dataType': 'aggregate'
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time

        try:
            response = self.session.get(self.base_url, params=params)
            print(f"Request URL: {response.url}")
            response.raise_for_status()
            
            response_data = response.json()
            
            # Handle new API response format
            if response_data.get('success') and 'data' in response_data and 'klineInfos' in response_data['data']:
                data = response_data['data']['klineInfos']
            elif 'klineInfos' in response_data and isinstance(response_data['klineInfos'], list):
                data = response_data['klineInfos']
            elif response_data.get('success') and 'data' in response_data:
                data = response_data['data']
            elif isinstance(response_data, list):
                data = response_data
            else:
                print(f"Unexpected response format for {token_info['symbol']}: {response_data}", file=sys.stderr)
                return []
            
            # Convert klines data to structured format
            if isinstance(data, list):
                klines_data = []
                for kline in data:
                    if isinstance(kline, list) and len(kline) >= 6:
                        klines_data.append({
                            'open_time': kline[0],
                            'open': float(kline[1]),
                            'high': float(kline[2]), 
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5]),
                            'close_time': kline[6] if len(kline) > 6 else None,
                            'quote_volume': float(kline[7]) if len(kline) > 7 else None,
                            'count': int(kline[8]) if len(kline) > 8 else None,
                            'taker_buy_volume': float(kline[9]) if len(kline) > 9 else None,
                            'taker_buy_quote_volume': float(kline[10]) if len(kline) > 10 else None,
                            'symbol': token_info['symbol'],
                            'alpha_id': token_info['alpha_id'],
                            'token_id': token_info['token_id'],
                            'interval': interval,
                            'timestamp': datetime.fromtimestamp(int(kline[0])/1000).isoformat() if kline[0] else None
                        })
                
                # If we only found response wrapper, return original format for debugging
                if not klines_data and len(data) == 0:
                    return [response_data]
                    
                return klines_data
            else:
                print(f"Data is not in expected list format for {token_info['symbol']}", file=sys.stderr)
                return [response_data]  # Return for debugging
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {token_info['symbol']}: {e}", file=sys.stderr)
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for {token_info['symbol']}: {e}", file=sys.stderr)
            return []

    def _parse_time(self, time_str: str) -> int:
        """Convert time string to timestamp"""
        try:
            # Try parsing as timestamp first
            return int(time_str)
        except ValueError:
            pass
        
        # Try different datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                return int(dt.timestamp() * 1000)
            except ValueError:
                continue
                
        raise ValueError(f"Invalid time format: {time_str}. Supported formats: YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, etc.")

    def to_csv(self, data: List[Dict], output_file: Optional[str] = None) -> None:
        """Convert data to CSV format"""
        if not data:
            print("No data to convert", file=sys.stderr)
            return

        # Determine CSV headers from first record
        headers = list(data[0].keys())
        
        # Write to file or stdout
        output = open(output_file, 'w', newline='') if output_file else sys.stdout
        
        try:
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        finally:
            if output_file:
                output.close()

    def to_freqtrade_format(self, data: List[Dict], output_file: str) -> None:
        """Convert data to freqtrade JSON format"""
        if not data:
            print("No data to convert", file=sys.stderr)
            return

        # Convert to freqtrade format: [timestamp_ms, open, high, low, close, volume]
        freqtrade_data = []
        for record in data:
            freqtrade_data.append([
                int(record['open_time']),  # timestamp in milliseconds
                record['open'],
                record['high'],
                record['low'],
                record['close'],
                record['volume']
            ])
        
        with open(output_file, 'w') as f:
            json.dump(freqtrade_data, f)
        
        print(f"Converted {len(freqtrade_data)} records to freqtrade format: {output_file}")

    def to_feather(self, data: List[Dict], output_dir: str, symbol: str, interval: str = "1h") -> None:
        """Convert data to feather format for FreqTrade"""
        if not data:
            print(f"No data to convert for {symbol}", file=sys.stderr)
            return

        # Convert to pandas DataFrame in FreqTrade format
        df_data = []
        for record in data:
            df_data.append({
                'date': pd.to_datetime(record['timestamp']).tz_localize('UTC'),
                'open': record['open'],
                'high': record['high'],
                'low': record['low'],
                'close': record['close'],
                'volume': record['volume']
            })
        
        df = pd.DataFrame(df_data)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as feather file with correct interval
        output_file = os.path.join(output_dir, f"{symbol}_USDT-{interval}.feather")
        df.to_feather(output_file)
        
        print(f"✓ Saved {len(df)} records for {symbol} to {output_file}")

    def fetch_data_with_pagination(self, token_info: Dict, interval: str = "1h", 
                                  total_limit: int = 500, start_time: Optional[int] = None, 
                                  end_time: Optional[int] = None) -> List[Dict]:
        """Fetch data with pagination to get more than 1000 records"""
        all_data = []
        current_end_time = end_time
        remaining_limit = total_limit
        
        while remaining_limit > 0:
            batch_limit = min(remaining_limit, 1000)
            
            print(f"Fetching batch: limit={batch_limit}, end_time={current_end_time}")
            batch_data = self.fetch_data(token_info, interval, batch_limit, start_time, current_end_time)
            
            if not batch_data:
                break
                
            all_data.extend(batch_data)
            remaining_limit -= len(batch_data)
            
            # 如果这批数据少于请求的数量，说明没有更多数据了
            if len(batch_data) < batch_limit:
                break
                
            # 更新end_time为最早记录的时间，用于下一次请求
            earliest_time = min(int(record['open_time']) for record in batch_data)
            current_end_time = earliest_time - 1  # 减1毫秒避免重复
            
            print(f"Got {len(batch_data)} records, total: {len(all_data)}, remaining: {remaining_limit}")
        
        # 按时间排序（最旧的在前）
        all_data.sort(key=lambda x: int(x['open_time']))
        return all_data

    def fetch_multiple_tokens(self, token_ids: List[int], interval: str = "1h", 
                             limit: int = 500, output_dir: str = "user_data/data/binance",
                             start_time: Optional[int] = None, end_time: Optional[int] = None) -> None:
        """Fetch data for multiple tokens and save as feather files"""
        tokens = self.get_token_info(token_ids)
        
        if not tokens:
            print("No valid tokens found for the given IDs")
            return
        
        # 如果没有指定时间范围，不设置时间参数
        if not start_time and not end_time:
            print(f"No time range specified, fetching latest available data")
        
        print(f"Fetching data for {len(tokens)} tokens...")
        
        for token in tokens:
            print(f"Fetching data for {token['symbol']} (ID: {token['token_id']})...")
            
            if limit > 1000:
                data = self.fetch_data_with_pagination(token, interval, limit, start_time, end_time)
            else:
                data = self.fetch_data(token, interval, limit, start_time, end_time)
            
            if data:
                self.to_feather(data, output_dir, token['symbol'], interval)
            else:
                print(f"✗ No data retrieved for {token['symbol']}")


def main():
    parser = argparse.ArgumentParser(description='Fetch Binance alpha token data and save as feather format')
    parser.add_argument('--token-ids', nargs='+', type=int, help='Token IDs from database (e.g., 2425111 2425112)')
    parser.add_argument('--interval', default='1h', help='Time interval (1h, 5m, 1d)')
    parser.add_argument('--limit', default=500, type=int, help='Number of records to fetch (will use pagination if > 1000)')
    parser.add_argument('--start-time', type=str, help='Start time (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-time', type=str, help='End time (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--days', type=int, default=30, help='Number of days to fetch (default: 30, used if no start/end time specified)')
    parser.add_argument('--output-dir', '-o', default='user_data/data/binance', help='Output directory for feather files')
    parser.add_argument('--list-tokens', action='store_true', help='List all available tokens with IDs')
    parser.add_argument('--symbol', help='Legacy: Alpha token symbol (e.g., ALPHA_428USDT)')
    parser.add_argument('--output', help='Legacy: Output CSV file')
    parser.add_argument('--test', action='store_true', help='Test API connection with a sample token')
    
    args = parser.parse_args()
    
    fetcher = AlphaDataFetcher()
    
    if args.list_tokens:
        tokens = fetcher.get_token_info()
        print(f"Available alpha tokens ({len(tokens)}):")
        for token in tokens:
            print(f"  ID: {token['token_id']}, Symbol: {token['symbol']}, Alpha: {token['alpha_id']}, Chain: {token['chain_id']}")
        return
    
    if args.test:
        # Test with a known token
        print("Testing API connection with a sample token...")
        test_tokens = fetcher.get_token_info([2425112])  # WBAI token
        if test_tokens:
            token = test_tokens[0]
            print(f"Testing with {token['symbol']} (ID: {token['token_id']})")
            data = fetcher.fetch_data(token, interval="1h", limit=10)
            if data:
                print(f"✓ Successfully fetched {len(data)} records")
                print("Sample record:", json.dumps(data[0], indent=2))
            else:
                print("✗ Failed to fetch data")
        else:
            print("✗ No test token found")
        return
    
    # Handle new batch mode
    if args.token_ids:
        start_time = None
        end_time = None
        
        # 解析时间参数
        if args.start_time:
            start_time = fetcher._parse_time(args.start_time)
        if args.end_time:
            end_time = fetcher._parse_time(args.end_time)
        
        # 如果没有指定时间范围，不设置时间限制让API返回最新数据
        if not start_time and not end_time and False:  # 暂时禁用自动时间范围
            now = datetime.now()
            end_time = int(now.timestamp() * 1000)
            start_time = int((now - timedelta(days=args.days)).timestamp() * 1000)
            print(f"Using default time range: last {args.days} days ({datetime.fromtimestamp(start_time/1000)} to {datetime.fromtimestamp(end_time/1000)})")
        
        fetcher.fetch_multiple_tokens(
            token_ids=args.token_ids,
            interval=args.interval,
            limit=args.limit,
            output_dir=args.output_dir,
            start_time=start_time,
            end_time=end_time
        )
        return
    
    # Legacy support for single symbol mode
    if args.symbol:
        print("Legacy mode: Converting symbol to new format...")
        # Extract alpha_id from symbol (e.g., ALPHA_428USDT -> ALPHA_428)
        if args.symbol.endswith('USDT'):
            alpha_id = args.symbol[:-4]
            tokens = fetcher.get_token_info()
            matching_token = None
            for token in tokens:
                if token['alpha_id'] == alpha_id:
                    matching_token = token
                    break
            
            if matching_token:
                print(f"Found matching token: {matching_token['symbol']} (ID: {matching_token['token_id']})")
                data = fetcher.fetch_data(matching_token, args.interval, args.limit or 500)
                if data:
                    if args.output:
                        fetcher.to_csv(data, args.output)
                        print(f"Data saved to {args.output}")
                    else:
                        fetcher.to_feather(data, args.output_dir, matching_token['symbol'], args.interval)
                else:
                    print("No data fetched")
                    sys.exit(1)
            else:
                print(f"No token found for alpha_id: {alpha_id}")
                sys.exit(1)
        else:
            print("Invalid symbol format. Use --list-tokens to see available options.")
            sys.exit(1)
        return
    
    # No valid arguments provided
    print("Error: Please specify --token-ids for batch mode or --symbol for legacy mode.")
    print("Use --list-tokens to see available options or --help for usage.")
    sys.exit(1)


if __name__ == '__main__':
    main()