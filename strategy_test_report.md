# Strategy Testing Report
**Tokens Tested**: 2 tokens from /Users/will9709/Desktop/1_m_listing_tokens.csv
**Test Method**: Individual 14-day periods from each token's listing time
**Generated**: 2025-10-24 12:07:03

## Token Test Periods

| Token | Listing Time | Test Start | Test End |
|-------|--------------|------------|----------|
| XPIN | 2025-10-20 | 2025-10-20 | 2025-11-03 |
| TGT | 2025-10-20 | 2025-10-20 | 2025-11-03 |

## Summary Table

| Token | Strategy | Timeframe | Regular Profit (%) | Optimized Profit (%) | Improvement | Total Trades | Win Rate (%) | Status |
|-------|----------|-----------|-------------------|---------------------|-------------|--------------|--------------|---------|
| XPIN | Strategy004_1m | 1m | -1.04 | 11.95 | +13.0% | 24 | 66.7 | ✅ Optimized |
| XPIN | Strategy004_5m | 5m | 2.72 | 15.5 | +12.8% | 12 | 66.7 | ✅ Optimized |
| XPIN | Bandtastic1m | 1m | -4.66 | 24.08 | +28.7% | 16 | 68.8 | ✅ Optimized |
| XPIN | Bandtastic5m | 5m | 0.0 | N/A | N/A | 0 | 0.0 | ✅ Regular |
| XPIN | AwesomeMacd1m | 1m | 13.16 | 29.06 | +15.9% | 58 | 60.3 | ✅ Optimized |
| XPIN | AwesomeMacd5m | 5m | -10.02 | 2.46 | +12.5% | 12 | 58.3 | ✅ Optimized |
| XPIN | BinHV271m | 1m | -2.3 | 8.81 | +11.1% | 3 | 100.0 | ✅ Optimized |
| XPIN | BinHV275m | 5m | 0.0 | N/A | N/A | 0 | 0.0 | ✅ Regular |
| XPIN | CofiBitStrategy1m | 1m | -21.19 | 5.49 | +26.7% | 60 | 66.7 | ✅ Optimized |
| XPIN | CofiBitStrategy5m | 5m | 13.16 | 15.5 | +2.3% | 6 | 100.0 | ✅ Optimized |
| XPIN | MACDStrategy1m | 1m | 22.27 | 53.78 | +31.5% | 45 | 55.6 | ✅ Optimized |
| XPIN | MACDStrategy5m | 5m | 2.2 | 30.85 | +28.7% | 9 | 100.0 | ✅ Optimized |
| XPIN | MACDStrategy_crossed1m | 1m | 5.01 | 5.83 | +0.8% | 8 | 100.0 | ✅ Optimized |
| XPIN | MACDStrategy_crossed5m | 5m | 0.0 | N/A | N/A | 0 | 0.0 | ✅ Regular |
| XPIN | UniversalMACD1m | 1m | 1.14 | 233.05 | +231.9% | 119 | 69.7 | ✅ Optimized |
| XPIN | UniversalMACD5m | 5m | 2.26 | 195.44 | +193.2% | 56 | 78.6 | ✅ Optimized |
| TGT | Strategy004_1m | 1m | -46.35 | 23.41 | +69.8% | 14 | 50.0 | ✅ Optimized |
| TGT | Strategy004_5m | 5m | 39.58 | 41.77 | +2.2% | 16 | 75.0 | ✅ Optimized |
| TGT | Bandtastic1m | 1m | -18.75 | N/A | N/A | 24 | 62.5 | ✅ Regular |
| TGT | Bandtastic5m | 5m | 2.4 | 2.4 | +0.0% | 2 | 50.0 | ✅ Optimized |
| TGT | AwesomeMacd1m | 1m | 3.76 | 28.65 | +24.9% | 41 | 58.5 | ✅ Optimized |
| TGT | AwesomeMacd5m | 5m | -23.79 | N/A | N/A | 14 | 21.4 | ✅ Regular |
| TGT | BinHV271m | 1m | 4.8 | 6.48 | +1.7% | 15 | 46.7 | ✅ Optimized |
| TGT | BinHV275m | 5m | 0.0 | N/A | N/A | 0 | 0.0 | ✅ Regular |
| TGT | CofiBitStrategy1m | 1m | -72.73 | N/A | N/A | 123 | 38.2 | ✅ Regular |
| TGT | CofiBitStrategy5m | 5m | 3.05 | 12.31 | +9.3% | 11 | 54.5 | ✅ Optimized |
| TGT | MACDStrategy1m | 1m | -24.81 | 10.09 | +34.9% | 33 | 72.7 | ✅ Optimized |
| TGT | MACDStrategy5m | 5m | 2.02 | 23.46 | +21.4% | 8 | 100.0 | ✅ Optimized |
| TGT | MACDStrategy_crossed1m | 1m | 6.21 | 31.66 | +25.4% | 20 | 50.0 | ✅ Optimized |
| TGT | MACDStrategy_crossed5m | 5m | 19.82 | 16.47 | -3.4% | 4 | 100.0 | ✅ Optimized |
| TGT | UniversalMACD1m | 1m | -18.21 | 56.3 | +74.5% | 67 | 67.2 | ✅ Optimized |
| TGT | UniversalMACD5m | 5m | 3.64 | 36.26 | +32.6% | 46 | 71.7 | ✅ Optimized |

## XPIN Detailed Results

### 📈 Successful Strategies (sorted by profit)

**UniversalMACD1m** (1m)
- *Description*: Universal MACD strategy
- *Regular Profit*: 1.14%
- *Optimized Profit*: 233.05%
- *Improvement*: +231.9%
- *Total Trades*: 119
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_umacd_max: 0.0121
  - buy_umacd_min: -0.02571
  - sell_umacd_max: -0.02323
  - sell_umacd_min: 0.03537
- *Win Rate*: 69.7%
- *Max Drawdown*: 21.06%
- *Avg Duration*: 0:39:00

**UniversalMACD5m** (5m)
- *Description*: Universal MACD strategy
- *Regular Profit*: 2.26%
- *Optimized Profit*: 195.44%
- *Improvement*: +193.2%
- *Total Trades*: 56
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_umacd_max: 0.0375
  - buy_umacd_min: -0.04669
  - sell_umacd_max: -0.01728
  - sell_umacd_min: 0.04364
- *Win Rate*: 78.6%
- *Max Drawdown*: 26.21%
- *Avg Duration*: 1:18:00

**MACDStrategy1m** (1m)
- *Description*: MACD strategy
- *Regular Profit*: 22.27%
- *Optimized Profit*: 53.78%
- *Improvement*: +31.5%
- *Total Trades*: 45
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_cci: -13
  - sell_cci: 546
- *Win Rate*: 55.6%
- *Max Drawdown*: 1.21%
- *Avg Duration*: 0:49:00

**MACDStrategy5m** (5m)
- *Description*: MACD strategy
- *Regular Profit*: 2.2%
- *Optimized Profit*: 30.85%
- *Improvement*: +28.7%
- *Total Trades*: 9
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_cci: -54
  - sell_cci: 486
- *Win Rate*: 100.0%
- *Max Drawdown*: 0.0%
- *Avg Duration*: 1:01:00

**AwesomeMacd1m** (1m)
- *Description*: Awesome oscillator + MACD
- *Regular Profit*: 13.16%
- *Optimized Profit*: 29.06%
- *Improvement*: +15.9%
- *Total Trades*: 58
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 0.841
  - buy_macd_threshold: 0.004
  - buy_rsi_threshold: 28
  - sell_bb_multiplier: 0.925
  - sell_macd_threshold: 0.02
  - sell_rsi_threshold: 68
- *Win Rate*: 60.3%
- *Max Drawdown*: 9.65%
- *Avg Duration*: 0:14:00

**Bandtastic1m** (1m)
- *Description*: Band-based trading strategy
- *Regular Profit*: -4.66%
- *Optimized Profit*: 24.08%
- *Improvement*: +28.7%
- *Total Trades*: 16
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_ema_enabled: False
  - buy_fastema: 76
  - buy_mfi: 37
  - buy_mfi_enabled: True
  - buy_rsi: 26
  - buy_rsi_enabled: False
  - buy_slowema: 76
  - buy_trigger: "bb_lower3"
  - sell_ema_enabled: True
  - sell_fastema: 314
  - sell_mfi: 37
  - sell_mfi_enabled: False
  - sell_rsi: 38
  - sell_rsi_enabled: False
  - sell_slowema: 235
  - sell_trigger: "sell-bb_upper2"
- *Win Rate*: 68.8%
- *Max Drawdown*: 2.38%
- *Avg Duration*: 0:13:00

**Strategy004_5m** (5m)
- *Description*: Strategy004 implementation
- *Regular Profit*: 2.72%
- *Optimized Profit*: 15.5%
- *Improvement*: +12.8%
- *Total Trades*: 12
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_adx: 35
  - buy_cci: -60
  - buy_fastd_th: 25
  - buy_fastk_th: 10
  - buy_slowadx: 15
  - buy_slowfastd_th: 36
  - buy_slowfastk_th: 29
  - buy_volume_th: 0.651
  - sell_fastd_th: 87
  - sell_fastk_th: 63
  - sell_slowadx: 17
- *Win Rate*: 66.7%
- *Max Drawdown*: 1.7%
- *Avg Duration*: 0:40:00

**CofiBitStrategy5m** (5m)
- *Description*: CofiBit trading strategy
- *Regular Profit*: 13.16%
- *Optimized Profit*: 15.5%
- *Improvement*: +2.3%
- *Total Trades*: 6
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_adx: 22
  - buy_fastx: 30
  - sell_fastx: 72
- *Win Rate*: 100.0%
- *Max Drawdown*: 0.0%
- *Avg Duration*: 0:31:00

**Strategy004_1m** (1m)
- *Description*: Strategy004 implementation
- *Regular Profit*: -1.04%
- *Optimized Profit*: 11.95%
- *Improvement*: +13.0%
- *Total Trades*: 24
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_adx: 46
  - buy_cci: -89
  - buy_fastd_th: 14
  - buy_fastk_th: 19
  - buy_slowadx: 26
  - buy_slowfastd_th: 29
  - buy_slowfastk_th: 24
  - buy_volume_th: 0.868
  - sell_fastd_th: 85
  - sell_fastk_th: 79
  - sell_slowadx: 17
- *Win Rate*: 66.7%
- *Max Drawdown*: 8.61%
- *Avg Duration*: 0:18:00

**BinHV271m** (1m)
- *Description*: Binary high volume v27
- *Regular Profit*: -2.3%
- *Optimized Profit*: 8.81%
- *Improvement*: +11.1%
- *Total Trades*: 3
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 1.071
  - buy_macd_threshold: -0.016
  - buy_rsi_threshold: 32
  - sell_bb_multiplier: 1.078
  - sell_macd_threshold: -0.018
  - sell_rsi_threshold: 62
- *Win Rate*: 100.0%
- *Max Drawdown*: 0.0%
- *Avg Duration*: 0:11:00

**MACDStrategy_crossed1m** (1m)
- *Description*: MACD crossover strategy
- *Regular Profit*: 5.01%
- *Optimized Profit*: 5.83%
- *Improvement*: +0.8%
- *Total Trades*: 8
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 0.928
  - buy_macd_threshold: -0.003
  - buy_rsi_threshold: 40
  - sell_bb_multiplier: 1.094
  - sell_macd_threshold: -0.007
  - sell_rsi_threshold: 72
- *Win Rate*: 100.0%
- *Max Drawdown*: 0.0%
- *Avg Duration*: 0:51:00

**CofiBitStrategy1m** (1m)
- *Description*: CofiBit trading strategy
- *Regular Profit*: -21.19%
- *Optimized Profit*: 5.49%
- *Improvement*: +26.7%
- *Total Trades*: 60
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_adx: 20
  - buy_fastx: 23
  - sell_fastx: 80
- *Win Rate*: 66.7%
- *Max Drawdown*: 13.43%
- *Avg Duration*: 0:07:00

**AwesomeMacd5m** (5m)
- *Description*: Awesome oscillator + MACD
- *Regular Profit*: -10.02%
- *Optimized Profit*: 2.46%
- *Improvement*: +12.5%
- *Total Trades*: 12
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 0.875
  - buy_macd_threshold: -0.012
  - buy_rsi_threshold: 25
  - sell_bb_multiplier: 0.807
  - sell_macd_threshold: -0.005
  - sell_rsi_threshold: 80
- *Win Rate*: 58.3%
- *Max Drawdown*: 7.0%
- *Avg Duration*: 0:44:00

**Bandtastic5m** (5m)
- *Description*: Band-based trading strategy
- *Total Profit*: 0.0%
- *Total Trades*: 0
- *Win Rate*: 0.0%
- *Max Drawdown*: N/A%
- *Avg Duration*: 0:00

**BinHV275m** (5m)
- *Description*: Binary high volume v27
- *Total Profit*: 0.0%
- *Total Trades*: 0
- *Win Rate*: 0.0%
- *Max Drawdown*: N/A%
- *Avg Duration*: 0:00

**MACDStrategy_crossed5m** (5m)
- *Description*: MACD crossover strategy
- *Total Profit*: 0.0%
- *Total Trades*: 0
- *Win Rate*: 0.0%
- *Max Drawdown*: N/A%
- *Avg Duration*: 0:00


## TGT Detailed Results

### 📈 Successful Strategies (sorted by profit)

**UniversalMACD1m** (1m)
- *Description*: Universal MACD strategy
- *Regular Profit*: -18.21%
- *Optimized Profit*: 56.3%
- *Improvement*: +74.5%
- *Total Trades*: 67
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_umacd_max: -0.00505
  - buy_umacd_min: -0.04607
  - sell_umacd_max: -0.01318
  - sell_umacd_min: -0.01616
- *Win Rate*: 67.2%
- *Max Drawdown*: 32.04%
- *Avg Duration*: 0:51:00

**Strategy004_5m** (5m)
- *Description*: Strategy004 implementation
- *Regular Profit*: 39.58%
- *Optimized Profit*: 41.77%
- *Improvement*: +2.2%
- *Total Trades*: 16
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_adx: 68
  - buy_cci: -56
  - buy_fastd_th: 27
  - buy_fastk_th: 10
  - buy_slowadx: 20
  - buy_slowfastd_th: 27
  - buy_slowfastk_th: 38
  - buy_volume_th: 1.355
  - sell_fastd_th: 74
  - sell_fastk_th: 60
  - sell_slowadx: 19
- *Win Rate*: 75.0%
- *Max Drawdown*: 1.19%
- *Avg Duration*: 2:12:00

**UniversalMACD5m** (5m)
- *Description*: Universal MACD strategy
- *Regular Profit*: 3.64%
- *Optimized Profit*: 36.26%
- *Improvement*: +32.6%
- *Total Trades*: 46
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_umacd_max: 0.03773
  - buy_umacd_min: -0.01409
  - sell_umacd_max: -0.02584
  - sell_umacd_min: -0.02823
- *Win Rate*: 71.7%
- *Max Drawdown*: 32.19%
- *Avg Duration*: 1:27:00

**MACDStrategy_crossed1m** (1m)
- *Description*: MACD crossover strategy
- *Regular Profit*: 6.21%
- *Optimized Profit*: 31.66%
- *Improvement*: +25.4%
- *Total Trades*: 20
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 0.859
  - buy_macd_threshold: -0.002
  - buy_rsi_threshold: 37
  - sell_bb_multiplier: 0.945
  - sell_macd_threshold: 0.016
  - sell_rsi_threshold: 65
- *Win Rate*: 50.0%
- *Max Drawdown*: 0.77%
- *Avg Duration*: 1:45:00

**AwesomeMacd1m** (1m)
- *Description*: Awesome oscillator + MACD
- *Regular Profit*: 3.76%
- *Optimized Profit*: 28.65%
- *Improvement*: +24.9%
- *Total Trades*: 41
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 0.998
  - buy_macd_threshold: -0.005
  - buy_rsi_threshold: 24
  - sell_bb_multiplier: 1.132
  - sell_macd_threshold: -0.006
  - sell_rsi_threshold: 77
- *Win Rate*: 58.5%
- *Max Drawdown*: 10.99%
- *Avg Duration*: 0:10:00

**MACDStrategy5m** (5m)
- *Description*: MACD strategy
- *Regular Profit*: 2.02%
- *Optimized Profit*: 23.46%
- *Improvement*: +21.4%
- *Total Trades*: 8
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_cci: -69
  - sell_cci: 675
- *Win Rate*: 100.0%
- *Max Drawdown*: 0.0%
- *Avg Duration*: 1:28:00

**Strategy004_1m** (1m)
- *Description*: Strategy004 implementation
- *Regular Profit*: -46.35%
- *Optimized Profit*: 23.41%
- *Improvement*: +69.8%
- *Total Trades*: 14
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_adx: 72
  - buy_cci: -176
  - buy_fastd_th: 23
  - buy_fastk_th: 16
  - buy_slowadx: 38
  - buy_slowfastd_th: 40
  - buy_slowfastk_th: 20
  - buy_volume_th: 0.569
  - sell_fastd_th: 83
  - sell_fastk_th: 84
  - sell_slowadx: 31
- *Win Rate*: 50.0%
- *Max Drawdown*: 0.23%
- *Avg Duration*: 1:09:00

**MACDStrategy_crossed5m** (5m)
- *Description*: MACD crossover strategy
- *Regular Profit*: 19.82%
- *Optimized Profit*: 16.47%
- *Improvement*: -3.4%
- *Total Trades*: 4
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 0.862
  - buy_macd_threshold: -0.004
  - buy_rsi_threshold: 36
  - sell_bb_multiplier: 0.955
  - sell_macd_threshold: -0.004
  - sell_rsi_threshold: 69
- *Win Rate*: 100.0%
- *Max Drawdown*: 0.0%
- *Avg Duration*: 1:25:00

**CofiBitStrategy5m** (5m)
- *Description*: CofiBit trading strategy
- *Regular Profit*: 3.05%
- *Optimized Profit*: 12.31%
- *Improvement*: +9.3%
- *Total Trades*: 11
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_adx: 29
  - buy_fastx: 28
  - sell_fastx: 78
- *Win Rate*: 54.5%
- *Max Drawdown*: 12.13%
- *Avg Duration*: 0:35:00

**MACDStrategy1m** (1m)
- *Description*: MACD strategy
- *Regular Profit*: -24.81%
- *Optimized Profit*: 10.09%
- *Improvement*: +34.9%
- *Total Trades*: 33
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_cci: -110
  - sell_cci: 249
- *Win Rate*: 72.7%
- *Max Drawdown*: 13.82%
- *Avg Duration*: 0:34:00

**BinHV271m** (1m)
- *Description*: Binary high volume v27
- *Regular Profit*: 4.8%
- *Optimized Profit*: 6.48%
- *Improvement*: +1.7%
- *Total Trades*: 15
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_bb_multiplier: 0.987
  - buy_macd_threshold: -0.02
  - buy_rsi_threshold: 31
  - sell_bb_multiplier: 0.926
  - sell_macd_threshold: -0.019
  - sell_rsi_threshold: 60
- *Win Rate*: 46.7%
- *Max Drawdown*: 14.68%
- *Avg Duration*: 0:33:00

**Bandtastic5m** (5m)
- *Description*: Band-based trading strategy
- *Regular Profit*: 2.4%
- *Optimized Profit*: 2.4%
- *Improvement*: +0.0%
- *Total Trades*: 2
- *Optimization Epochs*: 100
- *Best Objective*: N/A
- *Optimized Parameters*:
  - buy_ema_enabled: False
  - buy_fastema: 83
  - buy_mfi: 37
  - buy_mfi_enabled: False
  - buy_rsi: 67
  - buy_rsi_enabled: False
  - buy_slowema: 12
  - buy_trigger: "bb_lower1"
  - sell_ema_enabled: False
  - sell_fastema: 39
  - sell_mfi: 52
  - sell_mfi_enabled: False
  - sell_rsi: 58
  - sell_rsi_enabled: True
  - sell_slowema: 136
  - sell_trigger: "sell-bb_upper3"
- *Win Rate*: 50.0%
- *Max Drawdown*: 2.64%
- *Avg Duration*: 0:12:00

**BinHV275m** (5m)
- *Description*: Binary high volume v27
- *Total Profit*: 0.0%
- *Total Trades*: 0
- *Win Rate*: 0.0%
- *Max Drawdown*: N/A%
- *Avg Duration*: 0:00

**Bandtastic1m** (1m)
- *Description*: Band-based trading strategy
- *Total Profit*: -18.75%
- *Total Trades*: 24
- *Win Rate*: 62.5%
- *Max Drawdown*: 26.74%
- *Avg Duration*: 1:22:00

**AwesomeMacd5m** (5m)
- *Description*: Awesome oscillator + MACD
- *Total Profit*: -23.79%
- *Total Trades*: 14
- *Win Rate*: 21.4%
- *Max Drawdown*: 25.47%
- *Avg Duration*: 0:24:00

**CofiBitStrategy1m** (1m)
- *Description*: CofiBit trading strategy
- *Total Profit*: -72.73%
- *Total Trades*: 123
- *Win Rate*: 38.2%
- *Max Drawdown*: 75.04%
- *Avg Duration*: 0:09:00

## 🏆 Top Performing Strategies (All Tokens)

### By Total Profit

1. **UniversalMACD1m** on **XPIN** (Optimized) - 233.05% profit [+231.9%]
2. **UniversalMACD5m** on **XPIN** (Optimized) - 195.44% profit [+193.2%]
3. **UniversalMACD1m** on **TGT** (Optimized) - 56.3% profit [+74.5%]
4. **MACDStrategy1m** on **XPIN** (Optimized) - 53.78% profit [+31.5%]
5. **Strategy004_5m** on **TGT** (Optimized) - 41.77% profit [+2.2%]
6. **UniversalMACD5m** on **TGT** (Optimized) - 36.26% profit [+32.6%]
7. **MACDStrategy_crossed1m** on **TGT** (Optimized) - 31.66% profit [+25.4%]
8. **MACDStrategy5m** on **XPIN** (Optimized) - 30.85% profit [+28.7%]
9. **AwesomeMacd1m** on **XPIN** (Optimized) - 29.06% profit [+15.9%]
10. **AwesomeMacd1m** on **TGT** (Optimized) - 28.65% profit [+24.9%]

### By Win Rate (min 5 trades)

1. **MACDStrategy5m** on **XPIN** (Optimized) - 100.0% win rate (9 trades)
2. **MACDStrategy5m** on **TGT** (Optimized) - 100.0% win rate (8 trades)
3. **CofiBitStrategy5m** on **XPIN** (Optimized) - 100.0% win rate (6 trades)
4. **MACDStrategy_crossed1m** on **XPIN** (Optimized) - 100.0% win rate (8 trades)
5. **UniversalMACD5m** on **XPIN** (Optimized) - 78.6% win rate (56 trades)
6. **Strategy004_5m** on **TGT** (Optimized) - 75.0% win rate (16 trades)
7. **MACDStrategy1m** on **TGT** (Optimized) - 72.7% win rate (33 trades)
8. **UniversalMACD5m** on **TGT** (Optimized) - 71.7% win rate (46 trades)
9. **UniversalMACD1m** on **XPIN** (Optimized) - 69.7% win rate (119 trades)
10. **Bandtastic1m** on **XPIN** (Optimized) - 68.8% win rate (16 trades)

### 🚀 Biggest Optimization Improvements

1. **UniversalMACD1m** on **XPIN** - 1.1% → 233.1% (+231.9%)
   *Key params: buy_umacd_max: 0.0121, buy_umacd_min: -0.02571, sell_umacd_max: -0.02323*
2. **UniversalMACD5m** on **XPIN** - 2.3% → 195.4% (+193.2%)
   *Key params: buy_umacd_max: 0.0375, buy_umacd_min: -0.04669, sell_umacd_max: -0.01728*
3. **UniversalMACD1m** on **TGT** - -18.2% → 56.3% (+74.5%)
   *Key params: buy_umacd_max: -0.00505, buy_umacd_min: -0.04607, sell_umacd_max: -0.01318*
4. **Strategy004_1m** on **TGT** - -46.4% → 23.4% (+69.8%)
   *Key params: buy_adx: 72, buy_cci: -176, buy_fastd_th: 23*
5. **MACDStrategy1m** on **TGT** - -24.8% → 10.1% (+34.9%)
   *Key params: buy_cci: -110, sell_cci: 249*
6. **UniversalMACD5m** on **TGT** - 3.6% → 36.3% (+32.6%)
   *Key params: buy_umacd_max: 0.03773, buy_umacd_min: -0.01409, sell_umacd_max: -0.02584*
7. **MACDStrategy1m** on **XPIN** - 22.3% → 53.8% (+31.5%)
   *Key params: buy_cci: -13, sell_cci: 546*
8. **Bandtastic1m** on **XPIN** - -4.7% → 24.1% (+28.7%)
   *Key params: buy_ema_enabled: False, buy_fastema: 76, buy_mfi: 37*
9. **MACDStrategy5m** on **XPIN** - 2.2% → 30.9% (+28.7%)
   *Key params: buy_cci: -54, sell_cci: 486*
10. **CofiBitStrategy1m** on **XPIN** - -21.2% → 5.5% (+26.7%)
   *Key params: buy_adx: 20, buy_fastx: 23, sell_fastx: 80*