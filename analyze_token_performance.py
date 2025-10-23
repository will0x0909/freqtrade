#!/usr/bin/env python3
"""
Analyze token performance between 2025-09-21 and 2025-10-20
Classify tokens into three categories: up (+10%+), down (-10%-), sideways (±10%)
"""

import os
import pandas as pd
from datetime import datetime, date
import glob

def analyze_token_performance():
    data_dir = "user_data/data/binance/"
    start_date = "2025-09-21"
    end_date = "2025-10-20"
    
    results = []
    
    # Get all feather files
    files = glob.glob(os.path.join(data_dir, "*_USDT-1d.feather"))
    
    for file_path in files:
        try:
            # Extract token name from filename
            filename = os.path.basename(file_path)
            token_name = filename.replace("_USDT-1d.feather", "")
            
            # Read the data
            df = pd.read_feather(file_path)
            
            # Convert date column to date
            df['date'] = pd.to_datetime(df['date']).dt.date
            df = df.sort_values('date')
            
            # Filter data within our date range
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            # Get the first available date (if token listed after start_date)
            first_available = df['date'].min()
            if first_available > start_dt:
                actual_start_date = first_available
            else:
                actual_start_date = start_dt
            
            # Get start price (first available date)
            start_data = df[df['date'] >= actual_start_date].iloc[0] if len(df[df['date'] >= actual_start_date]) > 0 else None
            
            # Get end price (last date within range)
            end_data = df[df['date'] <= end_dt].iloc[-1] if len(df[df['date'] <= end_dt]) > 0 else None
            
            if start_data is not None and end_data is not None:
                start_price = float(start_data['close'])
                end_price = float(end_data['close'])
                
                # Calculate percentage change
                pct_change = ((end_price - start_price) / start_price) * 100
                
                # Classify
                if pct_change >= 10:
                    category = "上涨"
                elif pct_change <= -10:
                    category = "下跌"
                else:
                    category = "横盘"
                
                results.append({
                    'token': token_name,
                    'start_date': str(actual_start_date),
                    'end_date': str(end_data['date']),
                    'start_price': start_price,
                    'end_price': end_price,
                    'pct_change': pct_change,
                    'category': category
                })
                
                print(f"✓ {token_name}: {pct_change:.2f}% ({category})")
            else:
                print(f"✗ {token_name}: No valid data in date range")
                
        except Exception as e:
            print(f"✗ Error processing {token_name}: {e}")
    
    return results

def generate_markdown_report(results):
    # Sort results by category and percentage change
    results_df = pd.DataFrame(results)
    
    # Group by category
    up_tokens = results_df[results_df['category'] == '上涨'].sort_values('pct_change', ascending=False)
    down_tokens = results_df[results_df['category'] == '下跌'].sort_values('pct_change', ascending=True)
    sideways_tokens = results_df[results_df['category'] == '横盘'].sort_values('pct_change', ascending=False)
    
    # Generate markdown content
    md_content = f"""# Token Performance Analysis (2025-09-21 to 2025-10-20)

## Summary
- **Total tokens analyzed**: {len(results)}
- **上涨 (+10% or more)**: {len(up_tokens)} tokens
- **下跌 (-10% or less)**: {len(down_tokens)} tokens  
- **横盘 (±10%)**: {len(sideways_tokens)} tokens

---

## 🔥 上涨代币 ({len(up_tokens)} tokens)

| Token | Start Price | End Price | Change (%) | Start Date | End Date |
|-------|-------------|-----------|------------|------------|----------|
"""
    
    for _, row in up_tokens.iterrows():
        md_content += f"| {row['token']} | ${row['start_price']:.6f} | ${row['end_price']:.6f} | +{row['pct_change']:.2f}% | {row['start_date']} | {row['end_date']} |\n"
    
    md_content += f"""
---

## 📉 下跌代币 ({len(down_tokens)} tokens)

| Token | Start Price | End Price | Change (%) | Start Date | End Date |
|-------|-------------|-----------|------------|------------|----------|
"""
    
    for _, row in down_tokens.iterrows():
        md_content += f"| {row['token']} | ${row['start_price']:.6f} | ${row['end_price']:.6f} | {row['pct_change']:.2f}% | {row['start_date']} | {row['end_date']} |\n"
    
    md_content += f"""
---

## ↔️ 横盘代币 ({len(sideways_tokens)} tokens)

| Token | Start Price | End Price | Change (%) | Start Date | End Date |
|-------|-------------|-----------|------------|------------|----------|
"""
    
    for _, row in sideways_tokens.iterrows():
        md_content += f"| {row['token']} | ${row['start_price']:.6f} | ${row['end_price']:.6f} | {row['pct_change']:.2f}% | {row['start_date']} | {row['end_date']} |\n"
    
    md_content += f"""
---

## Analysis Details

**Methodology**: 
- Analysis period: 2025-09-21 to 2025-10-20
- For tokens listed after 2025-09-21, the first available trading date was used as the start date
- Classification criteria:
  - 上涨 (Up): +10% or higher
  - 下跌 (Down): -10% or lower  
  - 横盘 (Sideways): Between -10% and +10%

**Data Source**: Binance Alpha Trading data
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return md_content

if __name__ == "__main__":
    print("Starting token performance analysis...")
    results = analyze_token_performance()
    
    if len(results) > 0:
        print(f"\nGenerating markdown report for {len(results)} tokens...")
        md_content = generate_markdown_report(results)
        
        # Save to file
        with open("token_performance_analysis.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print("✓ Analysis complete! Report saved to token_performance_analysis.md")
    else:
        print("✗ No valid data found for analysis")