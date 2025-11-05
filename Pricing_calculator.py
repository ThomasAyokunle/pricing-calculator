# ==============================================================
# Laboratory Pricing Calculator (Google Sheet Integrated)
# ==============================================================

import streamlit as st
import pandas as pd
import math
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Laboratory Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Laboratory Pricing Calculator")
st.markdown("""
This calculator estimates and compares pricing scenarios for laboratory tests.  
It helps you understand how pricing, OPEX, and volume affect profitability.
""")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4"

def load_sheet(sheet_name):
    """Loads a Google Sheet as CSV and converts numeric columns safely."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

lab = st.sidebar.selectbox("Select Lab Location", ["OPIC_LAB", "CHEVRON_LAB"])
df = load_sheet(lab)

selected_test = st.sidebar.selectbox("Select Test", df["TEST NAME"].unique())
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 5.0, 1.5, 0.1)
custom_price = st.sidebar.number_input("Or Enter Proposed Price (₦)", min_value=0.0, value=0.0, step=500.0)
volume = st.sidebar.slider("Projected Volume", 1, 500, 100, 5)
opex_increase_rate = st.sidebar.slider("OPEX Volume Sensitivity (%)", 0, 100, 0, 5)

# --- FETCH TEST DETAILS ---
test = df[df["TEST NAME"] == selected_test].iloc[0]
current_price = float(test["CURRENT PRICE"])
cogs_per_test = float(test["COGS"])

# --- HELPER FUNCTION ---
def round100(value):
    try:
        return int(math.ceil(value / 100.0)) * 100
    except:
        return 0

# --- PRICE CALCULATIONS ---
proposed_price = custom_price if custom_price > 0 else cogs_per_test * markup
proposed_price = round100(proposed_price)

# --- CURRENT SCENARIO ---
current_revenue = current_price
current_cogs = cogs_per_test
current_gross_profit = current_revenue - current_cogs
base_opex = 0.25 * current_revenue  # 25% OPEX assumption
current_ebitda = current_gross_profit - base_opex
current_margin = round((current_ebitda / current_revenue) * 100, 1) if current_revenue != 0 else 0

# --- PROPOSED SCENARIO ---
proposed_revenue = proposed_price * volume
proposed_cogs = cogs_per_test * volume
proposed_gross_profit = proposed_revenue - proposed_cogs

# OPEX increases slightly with volume (logarithmic scaling)
opex_factor = 1 + (opex_increase_rate / 100)
proposed_opex = base_opex * (1 + 0.1 * math.log1p(volume / 50)) * opex_factor

proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1) if proposed_revenue != 0 else 0

# --- 20% MINIMUM MARGIN CHECK ---
min_required_price = (proposed_cogs + proposed_opex) / (1 - 0.2) / volume
if proposed_price < min_required_price:
    proposed_price = round100(min_required_price)
    proposed_revenue = proposed_price * volume
    proposed_gross_profit = proposed_revenue - proposed_cogs
    proposed_ebitda = proposed_gross_profit - proposed_opex
    proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1)
    price_note = "🔸 Adjusted upward to maintain ≥ 20% profit margin"
else:
    price_note = "✅ Within target margin range"

# --- ROUND KEY FIGURES ---
def r100(x): return round100(x)
current_revenue, proposed_revenue = r100(current_revenue), r100(proposed_revenue)
current_cogs, proposed_cogs = r100(current_cogs), r100(proposed_cogs)
base_opex, proposed_opex = r100(base_opex), r100(proposed_opex)
current_ebitda, proposed_ebitda = r100(current_ebitda), r100(proposed_ebitda)

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
st.subheader(f"Pricing Simulation: {selected_test}")

# Apply numeric formatting only to numeric columns
st.dataframe(
    comparison.style.format({
        "Current": "{:,.0f}",
        "Proposed": "{:,.0f}",
        "Change": "{:,.0f}"
    }),
    use_container_width=True
)

# --- TEST OVERVIEW TABLE (Current vs Proposed) ---
#df["PROPOSED PRICE"] = df["COGS"] * markup
#df["DIFFERENCE (₦)"] = df["PROPOSED PRICE"] - df["CURRENT PRICE"]

#overview = df[["TEST NAME", "CURRENT PRICE", "PROPOSED PRICE", "DIFFERENCE (₦)"]]
#overview["PROPOSED PRICE"] = overview["PROPOSED PRICE"].apply(round100)
#overview["DIFFERENCE (₦)"] = overview["DIFFERENCE (₦)"].apply(round100)

#st.subheader("Test Overview – Current vs Proposed Pricing")
# Format only numeric columns safely
#st.dataframe(
 #   overview.style.format({
  #      col: "{:,.0f}" for col in overview.select_dtypes(include=["number"]).columns
   # }),
    #use_container_width=True
#)


# --- SUMMARY ---
st.markdown(f"""
**Summary Insight**  
At a proposed price of **₦{proposed_price:,.0f}**, revenue and COGS scale with **{volume} tests**.  
EBITDA margin moves from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**.  
OPEX increases by **{opex_increase_rate}%** sensitivity for higher volumes, rising from 
₦{base_opex:,.0f} to ₦{proposed_opex:,.0f}.  
{price_note}
""")

# --- VOLUME SIMULATION (EBITDA vs Volume) ---
st.subheader("Volume Projection (EBITDA Impact)")

projection = pd.DataFrame({
    "Volume": range(1, volume + 1),
    "Total Revenue": [proposed_price * v for v in range(1, volume + 1)],
    "Total EBITDA": [
        (proposed_price * v - cogs_per_test * v -
         0.25 * proposed_price * v * (1 + (opex_increase_rate / 100)))
        for v in range(1, volume + 1)
    ]
})
st.line_chart(projection.set_index("Volume"))

# --- FOOTER ---
st.caption("💡 *Opex Sensitivity controls how much operating cost grows as volume increases.*")
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:14px;'>Created by <b>Ayokunle Thomas</b> – Data Scientist</p>",
    unsafe_allow_html=True
)
st.caption("ExCare Services Laboratory Pricing Calculator © 2025")




