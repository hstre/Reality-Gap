#!/usr/bin/env python3
"""
Reality Gap - Follow-up tests for Chinese data sources
"""
import sys, types

m = types.ModuleType('jsonpath')
sys.modules['jsonpath'] = m

import warnings
warnings.filterwarnings('ignore')
import pandas as pd

print("=" * 70)
print("FOLLOW-UP TEST A: AKShare Sina Balance Sheet - Date Depth")
print("=" * 70)

import akshare as ak

# Check Sina balance sheet date range for Moutai
try:
    df_bs = ak.stock_financial_report_sina(stock="sh600519", symbol="资产负债表")
    print(f"Shape: {df_bs.shape}")
    print(f"Report dates (报告日) - all:")
    dates = df_bs['报告日'].tolist()
    print(f"  Earliest: {min(dates)}")
    print(f"  Latest: {max(dates)}")
    print(f"  All dates: {sorted(dates)[:10]} ... {sorted(dates)[-5:]}")

    # Check key RG fields
    key_fields = {
        '商誉': 'Goodwill',
        '无形资产': 'Intangible Assets',
        '归属于母公司股东权益合计': 'Equity (Parent)',
        '所有者权益(或股东权益)合计': 'Total Equity',
        '实收资本(或股本)': 'Share Capital',
        '未分配利润': 'Retained Earnings',
    }
    print("\nKey RG balance sheet fields found:")
    for cn_name, en_name in key_fields.items():
        if cn_name in df_bs.columns:
            sample = df_bs[cn_name].dropna().head(3).tolist()
            print(f"  {en_name} ({cn_name}): found, sample={sample}")
        else:
            print(f"  {en_name} ({cn_name}): NOT FOUND")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 70)
print("FOLLOW-UP TEST B: AKShare Sina Income Statement - Date Depth & Net Income")
print("=" * 70)

try:
    df_inc = ak.stock_financial_report_sina(stock="sh600519", symbol="利润表")
    print(f"Shape: {df_inc.shape}")
    dates = df_inc['报告日'].tolist()
    print(f"  Earliest: {min(dates)}")
    print(f"  Latest: {max(dates)}")

    key_fields_inc = {
        '净利润': 'Net Income',
        '归属于母公司所有者的净利润': 'Net Income (Parent)',
        '营业总收入': 'Total Revenue',
        '利润总额': 'Pre-tax Income',
    }
    print("\nKey RG income fields found:")
    for cn_name, en_name in key_fields_inc.items():
        if cn_name in df_inc.columns:
            sample = df_inc[cn_name].dropna().head(3).tolist()
            print(f"  {en_name} ({cn_name}): found, sample={sample}")
        else:
            print(f"  {en_name} ({cn_name}): NOT FOUND")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 70)
print("FOLLOW-UP TEST C: stock_financial_abstract date depth & fields")
print("=" * 70)

try:
    df_abs = ak.stock_financial_abstract(symbol="600519")
    print(f"Shape: {df_abs.shape}")
    print(f"Rows (metrics): {df_abs['指标'].tolist()}")
    # Check which columns (dates) are available
    date_cols = [c for c in df_abs.columns if c not in ['选项', '指标']]
    print(f"  Total date periods: {len(date_cols)}")
    print(f"  Earliest: {min(date_cols)}")
    print(f"  Latest: {max(date_cols)}")

    # Find goodwill, equity, net income rows
    print("\nLooking for RG-relevant metrics:")
    for idx, row in df_abs.iterrows():
        metric = str(row['指标'])
        if any(term in metric for term in ['净利润', '商誉', '无形', '净资产', '股东', '权益', '总资产']):
            vals = row[date_cols[:5]].tolist()
            print(f"  [{row['选项']}] {metric}: {vals}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 70)
print("FOLLOW-UP TEST D: AKShare stock price via different function")
print("=" * 70)

# Try a2 different price functions since stock_zh_a_hist failed
try:
    # Try stock_zh_a_daily
    df_p = ak.stock_zh_a_daily(symbol="sh600519", adjust="hfq")
    print(f"stock_zh_a_daily shape: {df_p.shape}")
    print(f"Columns: {df_p.columns.tolist()}")
    print(f"Date range: {df_p.index.min()} to {df_p.index.max()}")
    print(df_p.head(3))
except AttributeError:
    print("stock_zh_a_daily: NOT FOUND")
except Exception as e:
    print(f"stock_zh_a_daily FAILED: {e}")

try:
    # Try stock_hk_hist for H-shares
    df_hk = ak.stock_hk_hist(symbol="00700", period="daily",
                               start_date="20100101", end_date="20231231",
                               adjust="hfq")
    print(f"\nstock_hk_hist 00700 shape: {df_hk.shape}")
    print(f"Columns: {df_hk.columns.tolist()}")
    if len(df_hk) > 0:
        print(f"Date range: {df_hk.iloc[0,0]} to {df_hk.iloc[-1,0]}")
except AttributeError:
    print("stock_hk_hist: NOT FOUND")
except Exception as e:
    print(f"stock_hk_hist FAILED: {e}")

print("\n" + "=" * 70)
print("FOLLOW-UP TEST E: AKShare shares outstanding / market cap")
print("=" * 70)

# Try individual stock fundamental info
funcs_to_try = [
    ("stock_individual_info_em", {"symbol": "600519"}),
    ("stock_a_lg_indicator", {"symbol": "600519"}),
]
for func_name, kwargs in funcs_to_try:
    try:
        func = getattr(ak, func_name)
        result = func(**kwargs)
        if result is not None:
            print(f"\n{func_name}: shape={result.shape}")
            print(f"  Columns/Index: {result.columns.tolist() if hasattr(result, 'columns') else result.index.tolist()}")
            print(result.head(10).to_string())
        else:
            print(f"\n{func_name}: None")
    except AttributeError:
        print(f"\n{func_name}: NOT FOUND")
    except Exception as e:
        print(f"\n{func_name}: FAILED - {e}")

print("\n" + "=" * 70)
print("FOLLOW-UP TEST F: yfinance - verify full historical balance sheet depth")
print("=" * 70)

import yfinance as yf

# Check Tencent quarterly data
try:
    t = yf.Ticker("0700.HK")

    # Quarterly balance sheet
    qbs = t.quarterly_balance_sheet
    print(f"Tencent quarterly balance sheet shape: {qbs.shape}")
    print(f"Date columns: {qbs.columns.tolist()}")

    # Annual balance sheet - how far back?
    abs_sheet = t.balance_sheet
    print(f"\nTencent annual balance sheet dates: {abs_sheet.columns.tolist()}")

    # Check specific RG fields
    for field in ['Goodwill', 'Other Intangible Assets', 'Goodwill And Other Intangible Assets',
                  'Stockholders Equity', 'Common Stock Equity', 'Net Income']:
        if field in abs_sheet.index:
            print(f"  {field}: {abs_sheet.loc[field].tolist()}")
        else:
            print(f"  {field}: NOT IN BALANCE SHEET")

    # Check income statement dates
    inc = t.income_stmt
    print(f"\nTencent annual income stmt dates: {inc.columns.tolist()}")
    if 'Net Income' in inc.index:
        print(f"  Net Income: {inc.loc['Net Income'].tolist()}")

except Exception as e:
    print(f"FAILED: {e}")

# Check if yfinance has older annual data via a different approach
try:
    print("\n--- yfinance historical fundamentals depth test ---")
    # Annual = 4 years max for yfinance typically
    # Try financials property (older API)
    t2 = yf.Ticker("0700.HK")
    fin = t2.financials  # older alias
    print(f"t.financials shape: {fin.shape}")
    print(f"t.financials dates: {fin.columns.tolist()}")
except Exception as e:
    print(f"financials property FAILED: {e}")

print("\n" + "=" * 70)
print("FOLLOW-UP TEST G: Check BYD and ICBC via Sina (SZSE stock)")
print("=" * 70)

for stock_code, name in [("sz002594", "BYD"), ("sh601398", "ICBC")]:
    try:
        df_t = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")
        print(f"\n{name} ({stock_code}) balance sheet: shape={df_t.shape}")
        dates = df_t['报告日'].tolist()
        print(f"  Date range: {min(dates)} to {max(dates)}")
        # Check goodwill
        for term in ['商誉', '无形资产', '归属于母公司股东权益合计']:
            if term in df_t.columns:
                sample = df_t[term].dropna().head(2).tolist()
                print(f"  {term}: {sample}")
    except Exception as e:
        print(f"{name} ({stock_code}): FAILED - {e}")

print("\n" + "=" * 70)
print("FOLLOW-UP TESTS COMPLETE")
print("=" * 70)
