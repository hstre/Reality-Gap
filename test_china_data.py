#!/usr/bin/env python3
"""
Reality Gap - Chinese Equity Data Source Feasibility Test
"""
import sys, types

# Patch: akshare needs 'jsonpath' but only jsonpath-ng is installed
m = types.ModuleType('jsonpath')
sys.modules['jsonpath'] = m

import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("TEST 1: AKSHARE")
print("=" * 70)

try:
    import akshare as ak
    import pandas as pd
    print(f"AKShare version: {ak.__version__}")
except Exception as e:
    print(f"AKShare import FAILED: {e}")
    sys.exit(1)

# --- Test 1a: Historical prices for Moutai ---
print("\n--- Test 1a: Historical daily prices 600519 (Moutai) ---")
try:
    df = ak.stock_zh_a_hist(symbol="600519", period="daily",
                             start_date="20100101", end_date="20231231",
                             adjust="hfq")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Date range: {df.iloc[0,0]} to {df.iloc[-1,0]}")
    print(df.head(3).to_string())
except Exception as e:
    print(f"FAILED: {e}")

# --- Test 1b: Balance sheet via Sina ---
print("\n--- Test 1b: Balance sheet via Sina (sh600519) ---")
try:
    df_bs = ak.stock_financial_report_sina(stock="sh600519", symbol="资产负债表")
    if df_bs is not None:
        print(f"Shape: {df_bs.shape}")
        print(f"Columns: {df_bs.columns.tolist()}")
        print(df_bs.head(3).to_string())
    else:
        print("Result: None")
except Exception as e:
    print(f"FAILED: {e}")

# --- Test 1c: Income statement via Sina ---
print("\n--- Test 1c: Income statement via Sina (sh600519) ---")
try:
    df_inc = ak.stock_financial_report_sina(stock="sh600519", symbol="利润表")
    if df_inc is not None:
        print(f"Shape: {df_inc.shape}")
        print(f"Columns: {df_inc.columns.tolist()}")
        print(df_inc.head(3).to_string())
    else:
        print("Result: None")
except Exception as e:
    print(f"FAILED: {e}")

# --- Test 1d: BYD prices ---
print("\n--- Test 1d: Historical prices 002594 (BYD, SZSE) ---")
try:
    df_byd = ak.stock_zh_a_hist(symbol="002594", period="daily",
                                  start_date="20100101", end_date="20231231",
                                  adjust="hfq")
    print(f"Shape: {df_byd.shape}")
    print(f"Columns: {df_byd.columns.tolist()}")
    print(f"Date range: {df_byd.iloc[0,0]} to {df_byd.iloc[-1,0]}")
except Exception as e:
    print(f"FAILED: {e}")

# --- Test 1e: Market cap snapshot ---
print("\n--- Test 1e: Real-time market snapshot (spot_em) ---")
try:
    df_cap = ak.stock_zh_a_spot_em()
    print(f"Columns: {df_cap.columns.tolist()}")
    print(f"Total rows: {len(df_cap)}")
    row = df_cap[df_cap['代码'] == '600519']
    print(f"Moutai row:\n{row.to_string()}")
except Exception as e:
    print(f"FAILED: {e}")

# --- Test 1f: Eastmoney balance sheet ---
print("\n--- Test 1f: Eastmoney balance sheet (600519) ---")
try:
    df_em = ak.stock_balance_sheet_by_report_em(symbol="600519")
    if df_em is not None:
        print(f"Shape: {df_em.shape}")
        print(f"Columns: {df_em.columns.tolist()}")
        # Show first few rows and key columns
        print(df_em.head(3).to_string())
        # Search for key RG columns
        cols_lower = [str(c).lower() for c in df_em.columns]
        key_terms = ['商誉', '无形', '净资产', '股东权益', '归属', 'goodwill', 'intangible', 'equity']
        print("\nKey RG-related columns found:")
        for c in df_em.columns:
            cs = str(c)
            if any(t in cs for t in key_terms):
                print(f"  {c}")
    else:
        print("Result: None")
except Exception as e:
    print(f"FAILED: {e}")

# --- Test 1g: Eastmoney income statement ---
print("\n--- Test 1g: Eastmoney income statement (600519) ---")
try:
    df_em_inc = ak.stock_profit_sheet_by_report_em(symbol="600519")
    if df_em_inc is not None:
        print(f"Shape: {df_em_inc.shape}")
        print(f"Columns: {df_em_inc.columns.tolist()}")
        print(df_em_inc.head(3).to_string())
        key_terms_inc = ['净利润', '利润', '收入', 'income', 'profit', 'revenue']
        print("\nKey RG-related columns found:")
        for c in df_em_inc.columns:
            cs = str(c)
            if any(t in cs for t in key_terms_inc):
                print(f"  {c}")
    else:
        print("Result: None")
except Exception as e:
    print(f"FAILED: {e}")

# --- Test 1h: Try historical fundamentals for multiple tickers ---
print("\n--- Test 1h: Multi-stock balance sheet check ---")
tickers = [("600519", "Moutai"), ("601398", "ICBC"), ("002594", "BYD")]
for sym, name in tickers:
    try:
        df_t = ak.stock_balance_sheet_by_report_em(symbol=sym)
        if df_t is not None and len(df_t) > 0:
            # Check earliest date
            date_cols = [c for c in df_t.columns if '报告' in str(c) or 'date' in str(c).lower() or '日期' in str(c)]
            print(f"{name} ({sym}): shape={df_t.shape}, date_cols={date_cols}")
            if date_cols:
                print(f"  Date range: {df_t[date_cols[0]].min()} to {df_t[date_cols[0]].max()}")
        else:
            print(f"{name} ({sym}): None or empty")
    except Exception as e:
        print(f"{name} ({sym}): FAILED - {e}")

print("\n" + "=" * 70)
print("TEST 2: BAOSTOCK")
print("=" * 70)

try:
    import baostock as bs
    print("Baostock imported ok")
except Exception as e:
    print(f"Baostock import FAILED: {e}")
    bs = None

if bs:
    lg = bs.login()
    print(f"Login: error_code={lg.error_code}, msg={lg.error_msg}")

    # Test 2a: Daily prices
    print("\n--- Test 2a: Daily prices sh.600519 ---")
    try:
        rs = bs.query_history_k_data_plus("sh.600519",
            "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg",
            start_date="2005-01-01", end_date="2023-12-31",
            frequency="d", adjustflag="2")
        data = []
        while rs.error_code == '0' and rs.next():
            data.append(rs.get_row_data())
        df = pd.DataFrame(data, columns=rs.fields)
        print(f"Shape: {df.shape}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 2b: Quarterly profit data
    print("\n--- Test 2b: Quarterly profit data (2019 Q4) ---")
    try:
        rs_q = bs.query_profit_data(code="sh.600519", year=2019, quarter=4)
        data_q = []
        while rs_q.error_code == '0' and rs_q.next():
            data_q.append(rs_q.get_row_data())
        df_q = pd.DataFrame(data_q, columns=rs_q.fields)
        print(f"Fields: {df_q.columns.tolist()}")
        print(df_q.to_string())
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 2c: Growth data
    print("\n--- Test 2c: Growth data (2019 Q4) ---")
    try:
        rs_g = bs.query_growth_data(code="sh.600519", year=2019, quarter=4)
        data_g = []
        while rs_g.error_code == '0' and rs_g.next():
            data_g.append(rs_g.get_row_data())
        df_g = pd.DataFrame(data_g, columns=rs_g.fields)
        print(f"Fields: {df_g.columns.tolist()}")
        print(df_g.to_string())
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 2d: Dupont data
    print("\n--- Test 2d: Dupont data (2019 Q4) ---")
    try:
        rs_d = bs.query_dupont_data(code="sh.600519", year=2019, quarter=4)
        data_d = []
        while rs_d.error_code == '0' and rs_d.next():
            data_d.append(rs_d.get_row_data())
        df_d = pd.DataFrame(data_d, columns=rs_d.fields)
        print(f"Fields: {df_d.columns.tolist()}")
        print(df_d.to_string())
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 2e: Historical profit data (multiple years)
    print("\n--- Test 2e: Historical profit data (2010-2022) ---")
    try:
        years = [2010, 2012, 2015, 2018, 2020, 2022]
        rows = []
        last_fields = []
        for yr in years:
            rs_p = bs.query_profit_data(code="sh.600519", year=yr, quarter=4)
            last_fields = rs_p.fields
            while rs_p.error_code == '0' and rs_p.next():
                rows.append(rs_p.get_row_data())
        df_hist = pd.DataFrame(rows, columns=last_fields if rows else [])
        print(f"Shape: {df_hist.shape}")
        print(df_hist.to_string())
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 2f: Balance sheet query
    print("\n--- Test 2f: Balance sheet data (2019 Q4) ---")
    try:
        rs_b = bs.query_balance_data(code="sh.600519", year=2019, quarter=4)
        data_b = []
        while rs_b.error_code == '0' and rs_b.next():
            data_b.append(rs_b.get_row_data())
        df_b = pd.DataFrame(data_b, columns=rs_b.fields)
        print(f"Fields: {df_b.columns.tolist()}")
        print(df_b.to_string())
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 2g: Cash flow data
    print("\n--- Test 2g: Cash flow data (2019 Q4) ---")
    try:
        rs_cf = bs.query_cash_flow_data(code="sh.600519", year=2019, quarter=4)
        data_cf = []
        while rs_cf.error_code == '0' and rs_cf.next():
            data_cf.append(rs_cf.get_row_data())
        df_cf = pd.DataFrame(data_cf, columns=rs_cf.fields)
        print(f"Fields: {df_cf.columns.tolist()}")
        print(df_cf.to_string())
    except Exception as e:
        print(f"FAILED: {e}")

    bs.logout()
    print("\nBaostock logout done")

print("\n" + "=" * 70)
print("TEST 3: TUSHARE PRO")
print("=" * 70)

try:
    import tushare as ts
    print(f"Tushare version: {ts.__version__}")
    ts.set_token('0')
    pro = ts.pro_api()

    try:
        df = pro.daily(ts_code='600519.SH', start_date='20100101', end_date='20231231')
        print(f"Tushare daily: {df.shape}")
    except Exception as e:
        print(f"Tushare daily FAILED: {e}")

    try:
        df = pro.income(ts_code='600519.SH', period='20231231')
        print(f"Tushare income: {df.shape}, columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"Tushare income FAILED: {e}")

    try:
        df = pro.balancesheet(ts_code='600519.SH', period='20231231')
        print(f"Tushare balancesheet: {df.shape}, columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"Tushare balancesheet FAILED: {e}")

except ImportError:
    print("Tushare NOT installed")
except Exception as e:
    print(f"Tushare setup FAILED: {e}")

print("\n" + "=" * 70)
print("TEST 4: YFINANCE - H-SHARES / HK-LISTED")
print("=" * 70)

try:
    import yfinance as yf
    print(f"yfinance version: {yf.__version__}")
except ImportError:
    print("yfinance NOT installed")
    yf = None

if yf:
    # Test 4a: Tencent HK
    print("\n--- Test 4a: Tencent 0700.HK ---")
    try:
        t = yf.Ticker("0700.HK")
        hist = t.history(start="2010-01-01", end="2023-12-31")
        print(f"Price shape: {hist.shape}")
        if len(hist) > 0:
            print(f"Date range: {hist.index.min().date()} to {hist.index.max().date()}")
            print(hist.head(3).to_string())
    except Exception as e:
        print(f"Prices FAILED: {e}")

    try:
        info = t.info
        print(f"sharesOutstanding: {info.get('sharesOutstanding')}")
        print(f"marketCap: {info.get('marketCap')}")
        print(f"currency: {info.get('currency')}")
    except Exception as e:
        print(f"Info FAILED: {e}")

    try:
        bs_sheet = t.balance_sheet
        print(f"\nBalance sheet shape: {bs_sheet.shape}")
        print(f"Balance sheet index (fields):\n{bs_sheet.index.tolist()}")
        print(f"Balance sheet columns (dates):\n{bs_sheet.columns.tolist()}")
        # Look for key RG fields
        key_terms = ['goodwill', 'intangible', 'equity', 'stockholder', 'tangible']
        print("\nKey RG fields in balance sheet:")
        for idx in bs_sheet.index:
            if any(t_kw in str(idx).lower() for t_kw in key_terms):
                print(f"  {idx}: {bs_sheet.loc[idx].tolist()}")
    except Exception as e:
        print(f"Balance sheet FAILED: {e}")

    try:
        inc = t.income_stmt
        print(f"\nIncome stmt shape: {inc.shape}")
        print(f"Income stmt index:\n{inc.index.tolist()}")
        key_terms_inc = ['net income', 'profit']
        print("\nKey RG fields in income stmt:")
        for idx in inc.index:
            if any(t_kw in str(idx).lower() for t_kw in key_terms_inc):
                print(f"  {idx}: {inc.loc[idx].tolist()}")
    except Exception as e:
        print(f"Income stmt FAILED: {e}")

    # Test 4b: Alibaba HK
    print("\n--- Test 4b: Alibaba 9988.HK ---")
    try:
        a = yf.Ticker("9988.HK")
        a_hist = a.history(start="2019-11-01", end="2023-12-31")
        print(f"Price shape: {a_hist.shape}")
        if len(a_hist) > 0:
            print(f"Date range: {a_hist.index.min().date()} to {a_hist.index.max().date()}")
        a_bs = a.balance_sheet
        print(f"Balance sheet shape: {a_bs.shape if a_bs is not None else 'None'}")
        if a_bs is not None and len(a_bs) > 0:
            print(f"Balance sheet index: {a_bs.index.tolist()}")
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 4c: China Mobile HK listing
    print("\n--- Test 4c: China Mobile 0941.HK ---")
    try:
        cm = yf.Ticker("0941.HK")
        cm_hist = cm.history(start="2005-01-01", end="2023-12-31")
        print(f"Price shape: {cm_hist.shape}")
        if len(cm_hist) > 0:
            print(f"Date range: {cm_hist.index.min().date()} to {cm_hist.index.max().date()}")
        cm_bs = cm.balance_sheet
        print(f"Balance sheet shape: {cm_bs.shape if cm_bs is not None else 'None'}")
    except Exception as e:
        print(f"FAILED: {e}")

print("\n" + "=" * 70)
print("TEST 5: AKSHARE - DEEPER FUNDAMENTALS EXPLORATION")
print("=" * 70)

# Test 5a: Check date depth of EM balance sheet
print("\n--- Test 5a: EM balance sheet date depth ---")
try:
    df_em_full = ak.stock_balance_sheet_by_report_em(symbol="600519")
    if df_em_full is not None and len(df_em_full) > 0:
        print(f"Total rows (periods): {len(df_em_full)}")
        # Find the date column
        for c in df_em_full.columns[:5]:
            print(f"  Col '{c}' first vals: {df_em_full[c].head(5).tolist()}")
        # Show full column list with Chinese names
        print(f"\nAll columns ({len(df_em_full.columns)}):")
        for i, c in enumerate(df_em_full.columns):
            print(f"  [{i}] {c}")
except Exception as e:
    print(f"FAILED: {e}")

# Test 5b: Check if goodwill and intangibles are in balance sheet
print("\n--- Test 5b: Check for goodwill/intangibles in EM balance sheet ---")
try:
    df_em_full = ak.stock_balance_sheet_by_report_em(symbol="600519")
    if df_em_full is not None and len(df_em_full) > 0:
        search_terms = ['商誉', '无形资产', '净资产', '股东权益', '归属母公司', '所有者权益']
        for term in search_terms:
            matching = [c for c in df_em_full.columns if term in str(c)]
            if matching:
                print(f"'{term}' found in: {matching}")
                for m in matching[:2]:
                    print(f"  {m}: {df_em_full[m].head(5).tolist()}")
            else:
                print(f"'{term}' NOT found")
except Exception as e:
    print(f"FAILED: {e}")

# Test 5c: Try alternative AKShare fundamental functions
print("\n--- Test 5c: Alternative AKShare fundamental functions ---")
alt_funcs = [
    ("stock_financial_abstract_ths", {"symbol": "600519", "indicator": "按报告期"}),
    ("stock_financial_abstract", {"symbol": "600519"}),
]
for func_name, kwargs in alt_funcs:
    try:
        func = getattr(ak, func_name)
        result = func(**kwargs)
        if result is not None:
            print(f"{func_name}: shape={result.shape}, cols={result.columns.tolist()[:10]}")
            print(result.head(3).to_string())
        else:
            print(f"{func_name}: None")
    except AttributeError:
        print(f"{func_name}: NOT FOUND in akshare {ak.__version__}")
    except Exception as e:
        print(f"{func_name}: FAILED - {e}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
