#!/usr/bin/env python3
"""
Script to fetch alpha token data from Binance API and convert to CSV format.
Supports time period and interval specification.
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import psycopg2


class AlphaDataFetcher:
    def __init__(self):
        self.base_url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/klines"
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

    def get_alpha_symbols(self) -> List[str]:
        """Get all available alpha token symbols from database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT alpha_id FROM tokens WHERE alpha_id IS NOT NULL ORDER BY alpha_id")
            symbols = [row[0] + "USDT" for row in cursor.fetchall()]
            conn.close()
            return symbols
        except Exception as e:
            print(f"Error fetching alpha symbols: {e}", file=sys.stderr)
            return []

    def fetch_data(self, 
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   interval: str = "15m",
                   symbol: Optional[str] = None) -> List[Dict]:
        """
        Fetch alpha token data from Binance API
        
        Args:
            start_time: Start time in format YYYY-MM-DD HH:MM:SS or timestamp
            end_time: End time in format YYYY-MM-DD HH:MM:SS or timestamp  
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            symbol: Alpha symbol like ALPHA_428USDT
        """
        if not symbol:
            print("Symbol is required for alpha token data", file=sys.stderr)
            return []

        params = {
            'interval': interval,
            'symbol': symbol
        }
        
        if start_time:
            params['startTime'] = self._parse_time(start_time)
        if end_time:
            params['endTime'] = self._parse_time(end_time)

        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Check if response is successful and extract data
            if response_data.get('success') and 'data' in response_data:
                data = response_data['data']
            elif isinstance(response_data, list):
                data = response_data
            else:
                print(f"Unexpected response format: {response_data}", file=sys.stderr)
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
                            'symbol': symbol,
                            'interval': interval,
                            'timestamp': datetime.fromtimestamp(int(kline[0])/1000).isoformat() if kline[0] else None
                        })
                return klines_data
            else:
                return [data] if data else []
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}", file=sys.stderr)
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}", file=sys.stderr)
            return []

    def _parse_time(self, time_str: str) -> int:
        """Convert time string to timestamp"""
        try:
            # Try parsing as timestamp first
            return int(time_str)
        except ValueError:
            pass
        
        try:
            # Try parsing as datetime string
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            return int(dt.timestamp() * 1000)
        except ValueError:
            try:
                # Try parsing as date only
                dt = datetime.strptime(time_str, '%Y-%m-%d')
                return int(dt.timestamp() * 1000)
            except ValueError:
                raise ValueError(f"Invalid time format: {time_str}")

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

    def get_recent_data(self, hours: int = 24, interval: str = '15m', symbol: str = None) -> List[Dict]:
        """Get recent data for specified number of hours"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        return self.fetch_data(
            start_time=start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time=end_time.strftime('%Y-%m-%d %H:%M:%S'),
            interval=interval,
            symbol=symbol
        )


def main():
    parser = argparse.ArgumentParser(description='Fetch Binance alpha token data')
    parser.add_argument('--start-time', help='Start time (YYYY-MM-DD HH:MM:SS or timestamp)')
    parser.add_argument('--end-time', help='End time (YYYY-MM-DD HH:MM:SS or timestamp)')
    parser.add_argument('--interval', default='15m', help='Time interval (1m, 5m, 15m, 1h, 4h, 1d)')
    parser.add_argument('--symbol', help='Alpha token symbol (e.g., ALPHA_428USDT)')
    parser.add_argument('--output', '-o', help='Output CSV file (default: stdout)')
    parser.add_argument('--recent-hours', type=int, help='Fetch recent N hours of data')
    parser.add_argument('--list-symbols', action='store_true', help='List all available alpha symbols')
    parser.add_argument('--test', action='store_true', help='Test API connection with ALPHA_428USDT')
    
    args = parser.parse_args()
    
    fetcher = AlphaDataFetcher()
    
    if args.list_symbols:
        symbols = fetcher.get_alpha_symbols()
        print(f"Available alpha symbols ({len(symbols)}):")
        for symbol in symbols:
            print(f"  {symbol}")
        return
    
    if args.test:
        print("Testing API connection with ALPHA_428USDT...")
        data = fetcher.fetch_data(symbol="ALPHA_428USDT", interval="15m")
        if data:
            print(f"✓ Successfully fetched {len(data)} records")
            print("Sample record:", json.dumps(data[0], indent=2))
        else:
            print("✗ Failed to fetch data")
        return
    
    if not args.symbol:
        print("Error: --symbol is required. Use --list-symbols to see available options.")
        sys.exit(1)
    
    if args.recent_hours:
        data = fetcher.get_recent_data(
            hours=args.recent_hours,
            interval=args.interval,
            symbol=args.symbol
        )
    else:
        data = fetcher.fetch_data(
            start_time=args.start_time,
            end_time=args.end_time,
            interval=args.interval,
            symbol=args.symbol
        )
    
    if data:
        fetcher.to_csv(data, args.output)
        if args.output:
            print(f"Data saved to {args.output}")
    else:
        print("No data fetched")
        sys.exit(1)


if __name__ == '__main__':
    main()