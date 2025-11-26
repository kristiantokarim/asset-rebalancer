import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"
st.set_page_config(page_title="Portfolio Pro", layout="wide")

# API Helpers
def fetch_all():
    p = requests.get(f"{API_URL}/portfolio").json()
    tickers = [a['ticker'] for a in p['assets']]
    currs = list(p['cash_balances'].keys())
    m = requests.get(f"{API_URL}/market-data", params={"tickers": ",".join(tickers), "currencies": ",".join(currs)}).json()
    return p, m

data, market = fetch_all()

# --- SIDEBAR ---
st.sidebar.header("💵 Cash")
for curr, amt in data["cash_balances"].items():
    data["cash_balances"][curr] = st.sidebar.number_input(f"{curr}", value=float(amt))

if st.sidebar.button("💾 Save Cash", use_container_width=True):
    requests.post(f"{API_URL}/save", json=data)
    st.rerun()

st.sidebar.divider()
if st.sidebar.button("⏮ Rollback", use_container_width=True):
    res = requests.post(f"{API_URL}/rollback")
    if res.status_code == 200:
        st.rerun()
    else:
        st.sidebar.error("No backups available.")

# --- CALCULATIONS ---
total_cash_usd = data['cash_balances']['USD']
for curr, amt in data['cash_balances'].items():
    if curr != "USD": total_cash_usd += (amt * market['fx'].get(f"{curr}USD=X", 1.0))

rows = []
total_mv, total_cost = 0.0, 0.0
for a in data['assets']:
    price = market['prices'].get(a['ticker'], 0.0)
    shares = sum(h['shares'] for h in a['holdings'])
    cost = sum(h['shares'] * h['avg_price'] for h in a['holdings'])
    mv = shares * price
    total_mv += mv
    total_cost += cost
    rows.append({"Ticker": a['ticker'], "Market Value": mv, "P/L": mv-cost, 
                 "Return %": (mv/cost-1)*100 if cost>0 else 0, "Target %": a['target_percent']})

full_nw = total_mv + total_cash_usd
df = pd.DataFrame(rows)
if not df.empty: df["Current %"] = (df["Market Value"] / full_nw * 100)

# --- DASHBOARD ---
st.title("📈 Performance Dashboard")
m1, m2, m3 = st.columns(3)
m1.metric("Net Worth", f"${full_nw:,.2f}")
m2.metric("Unrealized P/L", f"${(total_mv-total_cost):,.2f}", 
          delta=f"{(total_mv/total_cost-1)*100 if total_cost>0 else 0:.2f}%")
m3.metric("Buying Power (USD)", f"${total_cash_usd:,.2f}")

if not df.empty:
    st.dataframe(df.style.format({
        "Market Value": "{:,.2f}", "P/L": "{:,.2f}", "Return %": "{:.2f}%", 
        "Target %": "{:.2f}%", "Current %": "{:.2f}%"
    }).applymap(lambda x: 'color: #ff4b4b' if isinstance(x, float) and x < 0 else 'color: #00c781', 
                subset=['P/L', 'Return %']), use_container_width=True)

# --- VISUALS ---
st.divider()
v1, v2 = st.columns(2)
with v1:
    st.write("### Allocation")
    c_df = df[['Ticker', 'Market Value']].copy()
    c_df = pd.concat([c_df, pd.DataFrame([{"Ticker": "Cash", "Market Value": total_cash_usd}])])
    st.vega_lite_chart(c_df, {"mark": {"type": "arc", "innerRadius": 50}, 
                              "encoding": {"theta": {"field": "Market Value", "type": "quantitative"}, 
                                           "color": {"field": "Ticker", "type": "nominal"}}})

# --- REBALANCING ---
st.divider()
st.subheader("⚖️ One-Click Rebalance")
if total_cash_usd > 0 and not df.empty:
    alloc_cash = st.slider("Cash to Deploy", 0.0, float(total_cash_usd), float(total_cash_usd))
    df['Gap'] = ((df['Target %'] / 100 * full_nw) - df['Market Value']).clip(lower=0)
    total_gap = df['Gap'].sum()
    df['Buy $'] = (df['Gap'] / total_gap) * alloc_cash if total_gap > 0 else 0
    
    buys = df[df['Buy $'] > 1.0]
    if not buys.empty:
        trades = []
        for _, row in buys.iterrows():
            asset_ref = next(a for a in data['assets'] if a['ticker'] == row['Ticker'])
            acc_list = list(set(h['account'] for h in asset_ref['holdings'])) or ["Main"]
            r1, r2, r3 = st.columns([1, 1, 2])
            r1.write(row['Ticker'])
            r2.write(f"${row['Buy $']:,.2f}")
            sel_acc = r3.selectbox("Account", acc_list, key=f"re_{row['Ticker']}")
            trades.append({"ticker": row['Ticker'], "amount": row['Buy $'], "account": sel_acc, "price": market['prices'][row['Ticker']]})
        
        if st.button("🚀 Execute Trades", use_container_width=True):
            requests.post(f"{API_URL}/trade", json={"trades": trades})
            st.rerun()
