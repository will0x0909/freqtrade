# Strategy Testing Report
**Tokens Tested**: 2 tokens from /Users/will9709/Desktop/1_m_listing_tokens.csv
**Test Method**: Individual 14-day periods from each token's listing time
**Generated**: 2025-10-24 13:31:28

## Token Test Periods

| Token | Listing Time | Test Start | Test End |
|-------|--------------|------------|----------|
| XPIN | 2025-10-20 | 2025-10-20 | 2025-11-03 |
| TGT | 2025-10-20 | 2025-10-20 | 2025-11-03 |

## Summary Table

| Token | Strategy | Timeframe | Regular Profit (%) | Optimized Profit (%) | Improvement | Total Trades | Win Rate (%) | Status |
|-------|----------|-----------|-------------------|---------------------|-------------|--------------|--------------|---------|
| XPIN | UniversalMACD1m | 1m | 52.32 | 149.53 | +97.2% | 104 | 59.6 | ✅ Optimized |
| TGT | UniversalMACD1m | 1m | -1.15 | 48.45 | +49.6% | 90 | 70.0 | ✅ Optimized |

## XPIN Detailed Results

### 📈 Successful Strategies (sorted by profit)

**UniversalMACD1m** (1m)
- *Description*: Universal MACD strategy
- *Regular Profit*: 52.32%
- *Optimized Profit*: 149.53%
- *Improvement*: +97.2%
- *Total Trades*: 104
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_umacd_max: 0.03436
  - buy_umacd_min: -0.01467
  - sell_umacd_max: 0.00617
  - sell_umacd_min: 0.03962
- *Win Rate*: 59.6%
- *Max Drawdown*: 26.11%
- *Avg Duration*: 0:46:00


## TGT Detailed Results

### 📈 Successful Strategies (sorted by profit)

**UniversalMACD1m** (1m)
- *Description*: Universal MACD strategy
- *Regular Profit*: -1.15%
- *Optimized Profit*: 48.45%
- *Improvement*: +49.6%
- *Total Trades*: 90
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_umacd_max: 0.03902
  - buy_umacd_min: 0.01061
  - sell_umacd_max: -0.02482
  - sell_umacd_min: -0.03162
- *Win Rate*: 70.0%
- *Max Drawdown*: 50.69%
- *Avg Duration*: 0:44:00

## 🏆 Top Performing Strategies (All Tokens)

### By Total Profit

1. **UniversalMACD1m** on **XPIN** (Optimized) - 149.53% profit [+97.2%]
2. **UniversalMACD1m** on **TGT** (Optimized) - 48.45% profit [+49.6%]

### By Win Rate (min 5 trades)

1. **UniversalMACD1m** on **TGT** (Optimized) - 70.0% win rate (90 trades)
2. **UniversalMACD1m** on **XPIN** (Optimized) - 59.6% win rate (104 trades)

### 🚀 Biggest Optimization Improvements

1. **UniversalMACD1m** on **XPIN** - 52.3% → 149.5% (+97.2%)
   *Key params: buy_umacd_max: 0.03436, buy_umacd_min: -0.01467, sell_umacd_max: 0.00617*
2. **UniversalMACD1m** on **TGT** - -1.1% → 48.5% (+49.6%)
   *Key params: buy_umacd_max: 0.03902, buy_umacd_min: 0.01061, sell_umacd_max: -0.02482*