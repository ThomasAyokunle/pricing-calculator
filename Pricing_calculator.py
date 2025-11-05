# ==============================================================
# Laboratory Pricing Calculator (Volume-Adjusted COGS & Revenue)
# ==============================================================

import streamlit as st
import pandas as pd
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Laboratory Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("🧪 Laboratory Pricing Calculator")
st.markdown("""
This calculator estimates and compares pricing scenarios for laboratory tests.  
It emphasizes pricing impact on profitability, allowing OPEX, COGS, and revenue to scale 
appropriately with test volumes.
""")

# --- LOAD DATA FROM GOOGLE SHEETS ---
st.sidebar.header("⚙️ Simulation Controls")

sheet_url = "https://docs.google.com/spreadsheets/d/1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data(sheet_name):
    url = sheet_url + f"&sheet={sheet_name}"
    return pd.read_csv(url)

sheet_name = st.sidebar.selectbox("Select Laboratory", ["OPIC_LAB", "CHEVRON_LAB"])
df = load_data(sheet_name)

# Ensure numeric columns are floats
df["CURRENT PRICE"] = pd.to_numeric(df["CURRENT PRICE"], errors="coerce").fillna(0.0)
df["COGS"] = pd.to_numeric(df["COGS"], errors="coerce").fillna(0.0)

# --- SIDEBAR CONTROLS ---
selected_test = st.sidebar.selectbox("Select Test", df["TEST NAME"])
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 5.0, 1.5, 0.1)
custom_price = st.sidebar.number_input("Or Enter Proposed Price (₦)", min_value=0.0, value=0.0, step=500.0)
volume = st.sidebar.number_input("Projected Test Volume", 1, 500, 50)
opex_increase_rate = st.sidebar.slider("OPEX Volume Sensitivity (%)", 0, 100, 0)

# --- FETCH TEST DETAILS ---
test = df[df["TEST NAME"] == selected_test].iloc[0]
current_price = float(test["CURRENT PRICE"])
cogs_per_test = float(test["COGS"])

# --- SAFE CONVERSION HELPER ---
def to_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

def round100(value):
    return int(math.ceil(value / 100.0)) * 100

# --- PRICE CALCULATIONS WITH MINIMUM MARGIN ---
opex_sensitivity = 0.25  # base OPEX = 25% of revenue

if custom_price > 0:
    proposed_price = custom_price
else:
    # Step 1: Base markup
    base_price = cogs_per_test * markup

    # Step 2: OPEX per test
    opex_per_test = opex_sensitivity * base_price

    # Step 3: Calculate margin
    profit = base_price - cogs_per_test - opex_per_test
    net_margin = profit / base_price if base_price > 0 else 0

    # Step 4: Enforce minimum 20% net margin
    if net_margin < 0.20:
        base_price = (cogs_per_test + opex_per_test) / (1 - 0.20)
    
    proposed_price = base_price

# --- ROUND VALUES ---
proposed_price = round100(proposed_price)
current_price = round100(current_price)
cogs_per_test = round100(cogs_per_test)

# --- VOLUME-BASED CALCULATIONS ---
current_revenue = current_price
current_cogs = cogs_per_test
base_opex = 0.25 * current_revenue

proposed_revenue = proposed_price * volume
proposed_cogs = cogs_per_test * volume
opex_factor = 1 + (opex_increase_rate / 100)
proposed_opex = base_opex * (1 + 0.1 * math.log1p(volume / 50)) * opex_factor
proposed_gross_profit = proposed_revenue - proposed_cogs
proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1)

current_gross_profit = current_revenue - current_cogs
current_ebitda = current_gross_profit - base_opex
current_margin = round((current_ebitda / current_revenue) * 100, 1)

# --- COMPARISON TABLE ---
comparison = pd.DataFrame({
    "Metric": [
        "Revenue (₦)", "COGS (₦)", "Gross Profit (₦)",
        "OPEX (₦)", "EBITDA (₦)", "Profit Margin (%)"
    ],
    "Current": [
        current_revenue, current_cogs, current_gross_profit,
        base_opex, current_ebitda, current_margin
    ],
    "Proposed": [
        proposed_revenue, proposed_cogs, proposed_gross_profit,
        proposed_opex, proposed_ebitda, proposed_margin
    ],
    "Change": [
        proposed_revenue - current_revenue,
        proposed_cogs - current_cogs,
        proposed_gross_profit - current_gross_profit,
        proposed_opex - base_opex,
        proposed_ebitda - current_ebitda,
        round(proposed_margin - current_margin, 1)
    ]
})

# --- DISPLAY TABLE ---
st.subheader(f"📊 Pricing Simulation: {selected_test}")
numeric_cols = comparison.select_dtypes(include=['float64', 'int64']).columns
comparison[numeric_cols] = comparison[numeric_cols].apply(lambda x: x.round(0))

# Highlight EBITDA and Margin changes
def highlight_rows(row):
    if row["Metric"] in ["EBITDA (₦)", "Profit Margin (%)"]:
        return ["background-color: #fdd835; font-weight: bold;"] * len(row)
    return [""] * len(row)

st.dataframe(comparison.style.apply(highlight_rows, axis=1), use_container_width=True)

# --- SUMMARY ---
st.markdown(f"""
**💬 Summary Insight**  
At a proposed price of **₦{proposed_price:,.0f}**, revenue and COGS scale with test volume (**{volume} tests**).  
EBITDA margin shifts from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**.  
OPEX increases by {opex_increase_rate}% sensitivity for higher volumes, moving from 
₦{base_opex:,.0f} to ₦{proposed_opex:,.0f}.
""")

# --- EBITDA IMPACT VISUAL ---
st.subheader("📈 Volume Projection (EBITDA Impact)")

projection = pd.DataFrame({
    "Volume": range(1, volume + 1),
    "Total Revenue": [proposed_price * v for v in range(1, volume + 1)],
    "Total EBITDA": [
        (proposed_price * v - cogs_per_test * v - 0.25 * proposed_price * v * opex_factor)
        for v in range(1, volume + 1)
    ]
})
st.line_chart(projection.set_index("Volume"))

# --- FOOTER ---
st.markdown(
    "<hr style='margin-top:30px;'>"
    "<p style='text-align:center; color:#4CAF50; font-weight:bold;'>"
    "Created by <span style='color:#2E7D32;'>Ayokunle Thomas</span> — Data Scientist</p>",
    unsafe_allow_html=True
)
