#!/usr/bin/env python3
"""
Batch download script for alpha tokens using fetch_alpha_data.py
Downloads data for multiple tokens and timeframes
"""

import pandas as pd
import subprocess
import time
import sys
from datetime import datetime

class BatchAlphaDownloader:
    def __init__(self):
        self.token_ids_file = 'alpha_token_ids.csv'
        self.timeframes = ['1m']
        # 30天数据量计算: 1m=43200, 5m=8640, 1h=720
        self.limits = {
            '1m': 50000,   # 30天1分钟数据 + 余量
            # '5m': 10000,   # 30天5分钟数据 + 余量
            # '1h': 1000     # 30天1小时数据 + 余量
        }
        self.success_count = 0
        self.failure_count = 0
        
    def load_token_ids(self, limit=None):
        """Load token IDs from CSV file"""
        try:
            df = pd.read_csv(self.token_ids_file)
            token_ids = df['token_id'].astype(int).tolist()
            
            if limit:
                token_ids = token_ids[:limit]
                
            print(f"📊 Loaded {len(token_ids)} token IDs from {self.token_ids_file}")
            return token_ids
        except Exception as e:
            print(f"❌ Error loading token IDs: {e}")
            return []
    
    def download_batch(self, token_ids, timeframe, batch_size=10):
        """Download data for a batch of tokens using fetch_alpha_data.py"""
        print(f"\n🚀 Downloading {timeframe} data for {len(token_ids)} tokens (batch size: {batch_size})")
        
        # Process in batches
        for i in range(0, len(token_ids), batch_size):
            batch = token_ids[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(token_ids) + batch_size - 1) // batch_size
            
            print(f"\n📦 Batch {batch_num}/{total_batches}: Processing {len(batch)} tokens")
            print(f"   Token IDs: {batch}")
            
            # Build command for fetch_alpha_data.py
            limit = self.limits.get(timeframe, 1000)
            cmd = [
                'python', 'fetch_alpha_data.py',
                '--token-ids'] + [str(tid) for tid in batch] + [
                '--interval', timeframe,
                '--limit', str(limit)
            ]
            
            try:
                start_time = datetime.now()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                elapsed = datetime.now() - start_time
                
                if result.returncode == 0:
                    print(f"✅ Batch {batch_num} completed successfully in {elapsed}")
                    self.success_count += len(batch)
                    if result.stdout:
                        print(f"   Output: {result.stdout.strip()}")
                else:
                    print(f"❌ Batch {batch_num} failed")
                    self.failure_count += len(batch)
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()}")
                    if result.stdout:
                        print(f"   Output: {result.stdout.strip()}")
                        
            except subprocess.TimeoutExpired:
                print(f"⏰ Batch {batch_num} timeout")
                self.failure_count += len(batch)
            except Exception as e:
                print(f"💥 Batch {batch_num} exception: {e}")
                self.failure_count += len(batch)
            
            # Small delay between batches
            if i + batch_size < len(token_ids):
                time.sleep(2)
    
    def download_all_timeframes(self, token_ids, batch_size=10):
        """Download all timeframes for the given tokens"""
        print(f"\n{'='*60}")
        print(f"🎯 Starting batch download for {len(token_ids)} tokens")
        print(f"📊 Timeframes: {', '.join(self.timeframes)}")
        print(f"📦 Batch size: {batch_size}")
        # print(f"📈 Records per token: 1h={self.limits['1h']}, 5m={self.limits['5m']}, 1m={self.limits['1m']}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        for timeframe in self.timeframes:
            print(f"\n⏰ Processing timeframe: {timeframe}")
            self.download_batch(token_ids, timeframe, batch_size)
        
        elapsed = datetime.now() - start_time
        print(f"\n{'='*60}")
        print(f"🏁 Batch download completed!")
        print(f"⏰ Total time: {elapsed}")
        print(f"✅ Successful downloads: {self.success_count}")
        print(f"❌ Failed downloads: {self.failure_count}")
        print(f"{'='*60}")

def main():
    downloader = BatchAlphaDownloader()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Test with first 5 tokens
            token_ids = downloader.load_token_ids(limit=5)
            if token_ids:
                downloader.download_all_timeframes(token_ids, batch_size=5)
            return
        
        elif command == 'small':
            # Download first 20 tokens
            token_ids = downloader.load_token_ids(limit=20)
            if token_ids:
                downloader.download_all_timeframes(token_ids, batch_size=5)
            return
        
        elif command == 'medium':
            # Download first 50 tokens
            token_ids = downloader.load_token_ids(limit=50)
            if token_ids:
                downloader.download_all_timeframes(token_ids, batch_size=10)
            return
        
        elif command == 'large':
            # Download first 100 tokens
            token_ids = downloader.load_token_ids(limit=100)
            if token_ids:
                downloader.download_all_timeframes(token_ids, batch_size=10)
            return
        
        elif command == 'all':
            # Download all tokens
            token_ids = downloader.load_token_ids()
            if token_ids:
                downloader.download_all_timeframes(token_ids, batch_size=15)
            return
        
        else:
            print(f"❌ Unknown command: {command}")
    
    # Default: show help
    print("Batch Alpha Tokens Data Downloader")
    print("=" * 40)
    print("Usage:")
    print("  python batch_download_alpha_tokens.py test     - Download first 5 tokens (test)")
    print("  python batch_download_alpha_tokens.py small    - Download first 20 tokens")
    print("  python batch_download_alpha_tokens.py medium   - Download first 50 tokens")
    print("  python batch_download_alpha_tokens.py large    - Download first 100 tokens")
    print("  python batch_download_alpha_tokens.py all      - Download all tokens")
    print()
    print("Features:")
    print("  - Downloads 1h, 5m, 1m timeframes for each token")
    print("  - Processes tokens in batches to avoid API rate limits")
    print("  - Uses fetch_alpha_data.py for reliable data fetching")
    print()
    print("Examples:")
    print("  python batch_download_alpha_tokens.py test")
    print("  python batch_download_alpha_tokens.py small")

if __name__ == "__main__":
    main()