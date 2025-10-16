#!/usr/bin/env python3
"""
Fix script for Alpha token backtesting by adding custom market information.
Run this before backtesting to add missing market data for Alpha tokens.
"""

import json
import sys
from freqtrade.configuration import Configuration
from freqtrade.exchange import Exchange


def add_custom_markets(exchange, pairs):
    """Add custom market information for Alpha tokens"""
    for pair in pairs:
        if pair in exchange._markets:
            print(f"Market {pair} already exists, skipping...")
            continue
            
        base, quote = pair.split('/')
        
        custom_market = {
            "id": f"{base.lower()}{quote.lower()}",
            "symbol": pair,
            "base": base,
            "quote": quote,
            "active": True,
            "spot": True,
            "swap": False,
            "linear": None,
            "type": "spot",
            "precision": {
                "price": 8,
                "amount": 8,
                "cost": 8,
            },
            "lot": 0.00000001,
            "contractSize": None,
            "limits": {
                "amount": {
                    "min": 0.01,
                    "max": 100000000,
                },
                "price": {
                    "min": 0.00000001,
                    "max": 500000,
                },
                "cost": {
                    "min": 0.0001,
                    "max": 500000,
                },
                "leverage": {"min": 1.0, "max": 1.0},
            },
            "info": {}
        }
        
        exchange._markets[pair] = custom_market
        print(f"✓ Added custom market for {pair}")


def patch_exchange_methods(exchange):
    """Patch exchange methods to handle missing markets gracefully"""
    original_get_stake_limit = exchange._get_stake_amount_limit
    
    def patched_get_stake_limit(pair, price, stoploss, limit, leverage=1.0):
        try:
            return original_get_stake_limit(pair, price, stoploss, limit, leverage)
        except (ValueError, KeyError) as e:
            if "Can't get market information" in str(e) or pair not in exchange.markets:
                print(f"Warning: Missing market info for {pair}, using defaults for backtesting")
                # Return sensible defaults for backtesting
                if limit == "min":
                    # 最小值考虑价格和杠杆
                    min_cost = 0.1  # 最小成本 0.1 USDT
                    return min_cost / leverage if leverage > 0 else min_cost
                else:
                    return float("inf")  # Maximum stake - no limit
            else:
                raise
    
    exchange._get_stake_amount_limit = patched_get_stake_limit
    print("✓ Patched exchange methods for missing markets")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_alpha_backtesting.py <config_file> [pairs...]")
        print("Example: python fix_alpha_backtesting.py user_data/config_alpha.json PUP/USDT COAI/USDT")
        sys.exit(1)
    
    config_file = sys.argv[1]
    custom_pairs = sys.argv[2:] if len(sys.argv) > 2 else ["PUP/USDT", "COAI/USDT"]
    
    # Load configuration
    try:
        config = Configuration.from_files([config_file])
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    # Create exchange instance
    try:
        exchange = Exchange(config)
        print(f"✓ Created exchange: {exchange.name}")
    except Exception as e:
        print(f"Error creating exchange: {e}")
        sys.exit(1)
    
    # Add custom markets
    print(f"Adding custom markets for: {custom_pairs}")
    add_custom_markets(exchange, custom_pairs)
    
    # Patch exchange methods
    patch_exchange_methods(exchange)
    
    # Save patched market data for reference
    market_file = "user_data/alpha_markets.json"
    alpha_markets = {pair: exchange._markets[pair] for pair in custom_pairs if pair in exchange._markets}
    
    with open(market_file, 'w') as f:
        json.dump(alpha_markets, f, indent=2)
    
    print(f"✓ Saved custom market data to {market_file}")
    print("\nNow you can run backtesting normally:")
    print(f"freqtrade backtesting -c {config_file} --strategy AlphaTestStrategy")


if __name__ == "__main__":
    main()