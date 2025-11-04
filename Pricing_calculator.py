# ==============================================================
# Laboratory Pricing Calculator (Pricing-Focused + Scalable OPEX)
# ==============================================================

import streamlit as st
import pandas as pd
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Laboratory Pricing Calculator", layout="wide")

# --- HEADER ---
st.title("Laboratory Pricing Calculator")
st.markdown("""
This calculator helps estimate and compare pricing scenarios for laboratory tests.  
It emphasizes pricing impact on profitability while allowing OPEX to scale dynamically
based on revenue ratio and projected test volumes.
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
cogs = test["COGS"]

# --- HELPER FUNCTION (round to nearest 100) ---
def round100(value):
    return int(math.ceil(value / 100.0)) * 100

# --- OPEX CALCULATIONS ---
base_opex = 0.25 * current_price
proposed_opex = base_opex * (1 + (opex_increase_rate / 100) * (volume / 100))

# --- APPLY ROUNDING ---
base_opex = round100(base_opex)
proposed_opex = round100(proposed_opex)

# --- PRICE CALCULATIONS ---
if custom_price > 0:
    proposed_price = custom_price
else:
    proposed_price = cogs * markup

# --- ROUND PRICES ---
proposed_price = round100(proposed_price)
current_price = round100(current_price)
cogs = round100(cogs)

# --- METRICS ---
current_gross_profit = round100(current_price - cogs)
current_ebitda = round100(current_gross_profit - base_opex)
current_margin = round((current_ebitda / current_price) * 100, 1)

proposed_gross_profit = round100(proposed_price - cogs)
proposed_ebitda = round100(proposed_gross_profit - proposed_opex)
proposed_margin = round((proposed_ebitda / proposed_price) * 100, 1)

# --- COMPARISON TABLE ---
comparison = pd.DataFrame({
    "Metric": [
        "Selling Price (₦)", "COGS (₦)", "Gross Profit (₦)",
        "OPEX (₦)", "EBITDA (₦)", "Profit Margin (%)"
    ],
    "Current": [
        current_price, cogs, current_gross_profit,
        base_opex, current_ebitda, current_margin
    ],
    "Proposed": [
        proposed_price, cogs, proposed_gross_profit,
        proposed_opex, proposed_ebitda, proposed_margin
    ],
    "Change": [
        proposed_price - current_price, 0,
        proposed_gross_profit - current_gross_profit,
        proposed_opex - base_opex,
        proposed_ebitda - current_ebitda,
        round(proposed_margin - current_margin, 1)
    ]
})

# --- DISPLAY TABLE ---
st.subheader(f"Pricing Simulation: {selected_test}")
st.dataframe(comparison, use_container_width=True)

# --- SUMMARY SECTION ---
st.markdown(f"""
**Summary Insight**  
At a proposed selling price of **₦{proposed_price:,.0f}**, EBITDA margin changes from 
**{current_margin:.1f}%** to **{proposed_margin:.1f}%**.  
OPEX has adjusted from ₦{base_opex:,.0f} to ₦{proposed_opex:,.0f} due to an expected test volume of {volume},  
with a {opex_increase_rate}% OPEX sensitivity applied for volume scaling.
""")

# --- VOLUME SIMULATION ---
st.subheader("Volume Projection (EBITDA Impact)")

projection = pd.DataFrame({
    "Volume": range(1, volume + 1),
    "Total Revenue": [proposed_price * v for v in range(1, volume + 1)],
    "Total EBITDA": [proposed_ebitda * v for v in range(1, volume + 1)]
})
st.line_chart(projection.set_index("Volume"))

# --- FOOTER ---
st.caption("ExCare Services Laboratory Pricing Calculator © 2025")
