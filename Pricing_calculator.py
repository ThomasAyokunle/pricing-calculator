# ==============================================================
# Simple Laboratory Pricing Calculator
# ==============================================================

import streamlit as st
import pandas as pd
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="D-Rock Laboratory Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Laboratory Pricing Calculator")
st.markdown("Compare pricing scenarios to find the best price that meets your profit target.")

# --- GOOGLE SHEET SETUP ---
SHEET_ID = "1VAHAw4KVWuo-tP_rDlx3h_oYwypOodiJuZzhSYiX2v4"

def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

def round50(value):
    return int(round(value / 50.0)) * 50

# --- SIDEBAR: SIMPLE INPUTS ---
st.sidebar.header("Settings")

lab_location = st.sidebar.selectbox("Lab Location", ["OPICLAB", "CHEVRONLAB"])
df = load_sheet(lab_location)

test_name = st.sidebar.selectbox("Select Test", df["TEST NAME"].unique())
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 5.0, 1.5, 0.05,
    help="Quick pricing using a multiplier on cost. Example: 1.5× means 50% markup"
)
proposed_price = st.sidebar.number_input("Or Enter Proposed Price (₦)", min_value=0, value=0, step=50,
    help="Enter a specific price to override the markup calculation"
)
volume = st.sidebar.slider("Expected Volume (tests)", 0, 500, 20, 5,
    help="Total number of tests expected. Higher volumes may justify lower prices if partner commits to bulk orders"
)
opex_adjustment = st.sidebar.slider(
    "OPEX Adjustment (%)", 
    -20, 50, 0, 5,
    help="Adjust for efficiency gains or extra costs. Use negative % for bulk orders (e.g., -10% for committed volume), positive % for special requirements (e.g., +15% for specialized equipment)"
)
target_margin = st.sidebar.slider("Minimum Profit Margin (%)", 0, 50, 20, 1,
    help="Your minimum acceptable profit margin. Price will be flagged if it falls below this threshold"
)

# --- GET TEST DATA ---
test = df[df["TEST NAME"] == test_name].iloc[0]
current_price = float(test["CURRENT PRICE"])
cogs = float(test["COGS"])

# Get OPEX %
if "OPEX %" in df.columns:
    opex_rate = df["OPEX %"].dropna().iloc[0] / 100
else:
    opex_rate = 0.25

# --- CALCULATE PROPOSED PRICE ---
if proposed_price > 0:
    # Use custom price if entered
    proposed_price = round50(proposed_price)
else:
    # Use markup multiplier
    proposed_price = round50(cogs * markup)

# --- PER TEST CALCULATIONS ---
# Current
current_opex = opex_rate * current_price
current_profit = current_price - cogs - current_opex
current_margin = (current_profit / current_price * 100) if current_price > 0 else 0

# Proposed
proposed_opex = (opex_rate * proposed_price) * (1 + opex_adjustment / 100)
proposed_profit = proposed_price - cogs - proposed_opex
proposed_margin = (proposed_profit / proposed_price * 100) if proposed_price > 0 else 0

# Total (for volume)
total_revenue = proposed_price * volume
total_profit = proposed_profit * volume

# --- CHECK MINIMUM MARGIN ---
min_price_needed = (cogs + proposed_opex) / (1 - target_margin / 100)
margin_gap = proposed_price - min_price_needed

if margin_gap < 0:
    st.warning(f"⚠️ **Price below minimum threshold!** Need ₦{round50(min_price_needed):,.0f} to achieve {target_margin}% margin.")
    margin_status = "🔴 Below Target"
    status_color = "red"
    recommendation = f"Increase price to at least ₦{round50(min_price_needed):,.0f}"
elif margin_gap < 500:
    margin_status = "🟡 At Minimum"
    status_color = "orange"
    recommendation = "Price works but leaves little room for unexpected costs"
else:
    margin_status = "🟢 Healthy Margin"
    status_color = "green"
    recommendation = "Price is within target range"

# --- DISPLAY: KEY METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Proposed Price",
        f"₦{proposed_price:,.0f}",
        f"{((proposed_price - current_price) / current_price * 100):+.1f}% vs current"
    )

with col2:
    st.metric(
        "Net Margin",
        f"{proposed_margin:.1f}%",
        f"{(proposed_margin - current_margin):+.1f}%"
    )

with col3:
    st.metric(
        "Total Revenue",
        f"₦{total_revenue:,.0f}",
        f"{volume} tests"
    )

with col4:
    st.metric(
        "Total Profit",
        f"₦{total_profit:,.0f}",
        margin_status
    )

# --- DISPLAY: COMPARISON TABLE ---
st.markdown("---")
st.subheader("Per Test Economics")

# Calculate gross profit for display
current_gross_profit = current_price - cogs
proposed_gross_profit = proposed_price - cogs

comparison = pd.DataFrame({
    "Metric": [
        "Price per Test (₦)",
        "COGS per Test (₦)", 
        "Gross Profit per Test (₦)",
        "OPEX per Test (₦)",
        "EBITDA per Test (₦)",
        "Net Margin (%)"
    ],
    "Current": [
        round50(current_price),
        round50(cogs),
        round50(current_gross_profit),
        round50(current_opex),
        round50(current_profit),
        current_margin
    ],
    "Proposed": [
        round50(proposed_price),
        round50(cogs),
        round50(proposed_gross_profit),
        round50(proposed_opex),
        round50(proposed_profit),
        proposed_margin
    ],
    "Difference": [
        round50(proposed_price - current_price),
        0,  # COGS stays same per test
        round50(proposed_gross_profit - current_gross_profit),
        round50(proposed_opex - current_opex),
        round50(proposed_profit - current_profit),
        round(proposed_margin - current_margin, 1)
    ]
})

st.dataframe(
    comparison.style.format({
        "Current": "{:,.0f}",
        "Proposed": "{:,.0f}",
        "Difference": lambda x: f"{x:+,.0f}" if isinstance(x, (int, float)) else x
    }),
    use_container_width=True
)

# --- TOTAL VOLUME SUMMARY ---
st.subheader("Total Volume Impact")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Scenario Summary:**
    - **Volume**: {volume} units
    - **Price per Unit**: ₦{proposed_price_per_unit:,.0f}
    - **Total Revenue**: ₦{total_revenue:,.0f}
    - **Total EBITDA**: ₦{total_ebitda:,.0f}
    - **Net Margin**: {proposed_margin:.1f}%
    """)

with col2:
    st.markdown(f"""
    **Cost Breakdown:**
    - **Total COGS**: ₦{total_cogs:,.0f} ({(total_cogs/total_revenue*100):.1f}%)
    - **Total OPEX**: ₦{total_opex:,.0f} ({(total_opex/total_revenue*100):.1f}%)
    - **Gross Margin**: {((total_gross_profit/total_revenue)*100):.1f}%
    """)

# --- DISPLAY: RECOMMENDATION ---
st.markdown("---")
st.subheader("Recommendation")

if proposed_margin < target_margin:
    st.error(f"**{recommendation}** to reach {target_margin}% margin target.")
elif proposed_margin < target_margin + 5:
    st.warning(f"**{recommendation}** - Consider raising price by ₦50-100 for cushion.")
else:
    st.success(f"**{recommendation}** - You have {(proposed_margin - target_margin):.1f}% cushion above minimum.")

# --- VOLUME CHART ---
#st.markdown("---")
#st.subheader("📈 Profit at Different Volumes")

#volumes = list(range(1, max(volume, 100) + 1))
#profits = [proposed_profit * v for v in volumes]

#chart_data = pd.DataFrame({
 #   "Volume": volumes,
  #  "Total Profit (₦)": profits
#})

#st.line_chart(chart_data.set_index("Volume"))

# --- FOOTER ---
st.markdown("---")
st.caption("**Tip:** Adjust the proposed price to see how it affects profit margin and total profit.")
st.markdown(
    "<p style='text-align:center; font-size:14px;'>Created by <b>Ayokunle Thomas</b> – Data Scientist</p>",
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    .footer-links {
        text-align: center;
        font-size: 12px;
        font-style: italic;
        color: #888888;
    }
    .footer-links a {
        color: #888888;
        text-decoration: none;
        margin: 0 6px;
        transition: color 0.3s ease;
    }
    .footer-links a:hover {
        color: #1f77b4;
    }
    </style>
    <div class="footer-links">
        <a href="https://www.linkedin.com/in/ayokunle-thomas" target="_blank">LinkedIn</a> |
        <a href="https://github.com/ThomasAyokunle" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("D-Rock Laboratory Pricing Calculator © 2025")

