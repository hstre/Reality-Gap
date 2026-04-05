#!/usr/bin/env python3
"""
Reality Gap - Final targeted tests
"""
import sys, types
m = types.ModuleType('jsonpath')
sys.modules['jsonpath'] = m

import warnings
warnings.filterwarnings('ignore')
import pandas as pd

import akshare as ak

print("=" * 70)
print("TEST G: Moutai goodwill - check all historical values")
print("=" * 70)

try:
    df_bs = ak.stock_financial_report_sina(stock="sh600519", symbol="资产负债表")
    # Check goodwill column - non-null values
    gw = df_bs[['报告日', '商誉']].dropna(subset=['商誉'])
    print(f"Moutai goodwill non-null rows: {len(gw)}")
    print(gw.to_string() if len(gw) > 0 else "All goodwill values are NaN (Moutai has no goodwill)")

    ia = df_bs[['报告日', '无形资产']].dropna(subset=['无形资产'])
    print(f"\nMoutai intangibles non-null rows: {len(ia)}")
    if len(ia) > 0:
        print(f"  Earliest: {ia['报告日'].min()}, Latest: {ia['报告日'].max()}")
        print(ia.tail(5).to_string())

    eq = df_bs[['报告日', '归属于母公司股东权益合计']].dropna(subset=['归属于母公司股东权益合计'])
    print(f"\nMoutai parent equity non-null rows: {len(eq)}")
    print(f"  Earliest: {eq['报告日'].min()}, Latest: {eq['报告日'].max()}")
    print(eq.head(5).to_string())
    print(eq.tail(3).to_string())
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 70)
print("TEST H: Check AKShare stock price - different approach")
print("=" * 70)

# Try with eastmoney but different params
try:
    df_p = ak.stock_zh_a_hist(symbol="600519", period="daily",
                               start_date="20200101", end_date="20221231",
                               adjust="hfq")
    print(f"stock_zh_a_hist (2020-2022) shape: {df_p.shape}")
    print(df_p.head(3).to_string())
except Exception as e:
    print(f"stock_zh_a_hist failed: {e}")

# Check what price functions work
try:
    df_p2 = ak.stock_zh_a_hist_163(symbol="600519", start_date="20200101", end_date="20221231")
    print(f"\nstock_zh_a_hist_163 shape: {df_p2.shape}")
    print(df_p2.head(3).to_string())
except AttributeError:
    print("stock_zh_a_hist_163: NOT FOUND")
except Exception as e:
    print(f"stock_zh_a_hist_163 failed: {e}")

print("\n" + "=" * 70)
print("TEST I: Shares outstanding & historical market cap")
print("=" * 70)

# We have current shares from stock_individual_info_em
# But we need historical. Check if AKShare has it.
try:
    df_shares = ak.stock_zh_a_hist(symbol="600519", period="daily",
                                    start_date="20230101", end_date="20231231",
                                    adjust="")  # unadjusted
    print(f"Unadjusted prices shape: {df_shares.shape}")
    print(f"Columns: {df_shares.columns.tolist()}")
    if df_shares is not None and len(df_shares) > 0:
        print(df_shares.head(3).to_string())
except Exception as e:
    print(f"Unadjusted prices failed: {e}")

# Check stock_financial_abstract for shares data
try:
    df_abs = ak.stock_financial_abstract(symbol="600519")
    # Find shares-related rows
    for idx, row in df_abs.iterrows():
        metric = str(row['指标'])
        if any(term in metric for term in ['股本', '流通', '总股', '市值', '股数']):
            print(f"  [{row['选项']}] {metric}")
except Exception as e:
    print(f"stock_financial_abstract failed: {e}")

# Try to get historical share count from balance sheet
try:
    df_bs2 = ak.stock_financial_report_sina(stock="sh600519", symbol="资产负债表")
    share_col = df_bs2[['报告日', '实收资本(或股本)']].dropna()
    print(f"\nShare capital (paid-in capital, proxy for shares outstanding):")
    print(f"  Earliest: {share_col['报告日'].min()}")
    print(share_col.head(5).to_string())
    print(share_col.tail(5).to_string())
except Exception as e:
    print(f"Share capital check failed: {e}")

print("\n" + "=" * 70)
print("TEST J: Tushare - document behavior")
print("=" * 70)

try:
    import tushare as ts
    print(f"Tushare version: {ts.__version__}")

    # Test with placeholder token
    ts.set_token('0')
    pro = ts.pro_api()

    for endpoint, kwargs in [
        ("daily", {"ts_code": "600519.SH", "start_date": "20230101", "end_date": "20231231"}),
        ("income", {"ts_code": "600519.SH", "period": "20221231"}),
        ("balancesheet", {"ts_code": "600519.SH", "period": "20221231"}),
    ]:
        try:
            result = getattr(pro, endpoint)(**kwargs)
            print(f"{endpoint}: SUCCESS shape={result.shape}")
        except Exception as e:
            print(f"{endpoint}: FAILED - {str(e)[:100]}")

    # What fields does tushare balancesheet have (just check docs)?
    print("\nTushare balancesheet expected fields (from docs):")
    print("  goodwill, intan_assets, total_hldr_eqy_exc_min_int, net_profit, etc.")
    print("  Note: requires valid token (free registration at tushare.pro)")
    print("  Registration gives ~120 points/min rate limit")
    print("  Income/balance sheet data goes back to ~2007")
except ImportError:
    print("Tushare NOT installed")
except Exception as e:
    print(f"Tushare: {e}")

print("\n" + "=" * 70)
print("TEST K: yfinance quarterly data depth")
print("=" * 70)

import yfinance as yf

# Check how many years of quarterly data yfinance provides
for ticker, name in [("0700.HK", "Tencent"), ("9988.HK", "Alibaba HK"), ("0941.HK", "China Mobile")]:
    try:
        t = yf.Ticker(ticker)
        qbs = t.quarterly_balance_sheet
        qinc = t.quarterly_income_stmt
        abs_bs = t.balance_sheet
        print(f"\n{name} ({ticker}):")
        print(f"  Annual BS dates: {abs_bs.columns.tolist()}")
        print(f"  Quarterly BS dates: {qbs.columns.tolist()}")
        print(f"  Quarterly income dates: {qinc.columns.tolist()}")

        # Check RG fields exist
        has_gw = 'Goodwill' in abs_bs.index
        has_ia = 'Other Intangible Assets' in abs_bs.index
        has_eq = 'Stockholders Equity' in abs_bs.index or 'Common Stock Equity' in abs_bs.index
        has_ni = 'Net Income' in qinc.index
        print(f"  Goodwill: {has_gw}, Intangibles: {has_ia}, Equity: {has_eq}, Net Income: {has_ni}")
        if has_gw:
            print(f"    Goodwill values: {abs_bs.loc['Goodwill'].tolist()}")
        if has_ia:
            print(f"    Intangibles values: {abs_bs.loc['Other Intangible Assets'].tolist()}")
    except Exception as e:
        print(f"{name}: FAILED - {e}")

print("\n" + "=" * 70)
print("FINAL TESTS COMPLETE")
print("=" * 70)
