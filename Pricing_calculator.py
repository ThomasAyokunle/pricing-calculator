# ==============================================================
# Laboratory Pricing Calculator (Volume-Adjusted COGS & Revenue)
# ==============================================================

import streamlit as st
import pandas as pd
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Laboratory Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Laboratory Pricing Calculator")
st.markdown("""
This calculator estimates and compares pricing scenarios for laboratory tests.  
It emphasizes pricing impact on profitability, allowing OPEX, COGS, and revenue to scale 
appropriately with test volumes.
""")

# --- BASE DATA ---
data = {
    "Test Name": [
        "FBC", "Lipid Profile", "H.PYLORI", "URINE M/C/S", "HEPATITIS B SCREENING",
        "LIVER FUNCTION TEST", "MALARIA PARASITE SMEAR", "UREA AND CREATININE",
        "TYPHOID TEST", "PROGESTERONE", "TESTOSTERONE", "PROLACTIN", "HBA1C", "PSA"
    ],
    "Department": [
        "Haematology", "Chemistry", "Haematology", "Microbiology", "Haematology",
        "Chemistry", "Microbiology", "Chemistry", "Serology", "Hormones",
        "Hormones", "Hormones", "Chemistry", "Chemistry"
    ],
    "Current Price": [
        8000, 15000, 6000, 8000, 4000, 12000, 3000, 5000, 5000, 15000, 15000, 15000, 17400, 17400
    ],
    "COGS": [
        2000, 5333, 875, 2400, 500, 3600, 900, 1667, 1300, 6400, 6400, 6400, 6400, 6400
    ]
}
df = pd.DataFrame(data)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")

selected_test = st.sidebar.selectbox("Select Test", df["Test Name"])
markup = st.sidebar.slider("Markup Multiplier (×)", 1.0, 3.0, 1.5, 0.1)
custom_price = st.sidebar.number_input("Or Enter Proposed Price (₦)", min_value=0.0, value=0.0, step=500.0)
volume = st.sidebar.number_input("Projected Test Volume", 1, 500, 50)
opex_increase_rate = st.sidebar.slider("OPEX Volume Sensitivity (%)", 0, 50, 20)

# --- FETCH TEST DETAILS ---
test = df[df["Test Name"] == selected_test].iloc[0]
current_price = test["Current Price"]
cogs_per_test = test["COGS"]

# --- HELPER FUNCTION ---
def round100(value):
    return int(math.ceil(value / 100.0)) * 100

# --- PRICE CALCULATIONS ---
if custom_price > 0:
    proposed_price = custom_price
else:
    proposed_price = cogs_per_test * markup

# --- ROUND PRICES ---
proposed_price = round100(proposed_price)
current_price = round100(current_price)
cogs_per_test = round100(cogs_per_test)

# --- VOLUME-BASED CALCULATIONS ---
# Current scenario (single test basis * assumed base volume = 1)
current_revenue = current_price 
current_cogs = cogs_per_test

# --- OPEX CALCULATIONS (more realistic scaling) ---
# Base OPEX is 25% of current revenue
base_opex = 0.25 * current_revenue

# For proposed, OPEX rises slightly (not exponentially) with volume sensitivity
proposed_revenue = proposed_price * volume
proposed_cogs = cogs_per_test * volume
proposed_gross_profit = proposed_revenue - proposed_cogs

# Slight increase in OPEX — e.g., 25% × (1 + sensitivity%)
opex_factor = 1 + (opex_increase_rate / 100)
proposed_opex = base_opex * (1 + 0.1 * math.log1p(volume / 50))

# --- PROFITABILITY METRICS ---
current_gross_profit = current_revenue - current_cogs
current_ebitda = current_gross_profit - base_opex
current_margin = round((current_ebitda / current_revenue) * 100, 1)

proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1)

# --- PROFITABILITY METRICS ---
current_gross_profit = current_revenue - current_cogs
current_ebitda = current_gross_profit - base_opex
current_margin = round((current_ebitda / current_revenue) * 100, 1)

proposed_cogs = cogs_per_test * volume
proposed_gross_profit = proposed_revenue - proposed_cogs
proposed_ebitda = proposed_gross_profit - proposed_opex
proposed_margin = round((proposed_ebitda / proposed_revenue) * 100, 1)

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
# Ensure only numeric columns are formatted
numeric_cols = comparison.select_dtypes(include=['float64', 'int64']).columns
comparison[numeric_cols] = comparison[numeric_cols].apply(lambda x: x.round(0))

st.dataframe(comparison, use_container_width=True)


# --- SUMMARY ---
st.markdown(f"""
**Summary Insight**  
At a proposed price of **₦{proposed_price:,.0f}**, revenue and COGS scale with test volume (**{volume} tests**).  
EBITDA margin shifts from **{current_margin:.1f}%** to **{proposed_margin:.1f}%**.  
OPEX increases by {opex_increase_rate}% sensitivity for higher volumes, moving from 
₦{base_opex:,.0f} to ₦{proposed_opex:,.0f}.
""")

# --- VOLUME SIMULATION (EBITDA vs Volume) ---
st.subheader("Volume Projection (EBITDA Impact)")

projection = pd.DataFrame({
    "Volume": range(1, volume + 1),
    "Total Revenue": [proposed_price * v for v in range(1, volume + 1)],
    "Total EBITDA": [
        (proposed_price * v - cogs_per_test * v - 0.25 * proposed_price * v * opex_factor)
        for v in range(1, volume + 1)
    ]
})
st.line_chart(projection.set_index("Volume"))




