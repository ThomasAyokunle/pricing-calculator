import streamlit as st
import math

# --- Title ---
st.title("Test Pricing and Profitability Calculator")

st.write("""
Use this tool to review current and proposed pricing performance.  
Adjust price, volume, and opex assumptions to see how each affects profitability.
""")

# --- Input Section ---
st.header("Input Parameters")

col1, col2 = st.columns(2)
with col1:
    current_price = st.number_input("Current Price per Test (₦)", min_value=0, value=8000, step=500)
    cost_per_test = st.number_input("Cost per Test (₦)", min_value=0, value=6000, step=500)
    current_volume = st.number_input("Current Monthly Volume (Tests)", min_value=1, value=100)

with col2:
    proposed_price = st.number_input("Proposed Price per Test (₦)", min_value=0, value=9000, step=500)
    proposed_volume = st.number_input("Expected Monthly Volume (Tests)", min_value=1, value=150)
    volume_opex_adj = st.slider("Opex Adjustment (%) with Volume Increase", 0, 30, 10)

# --- Helper function ---
def round_up(value):
    return int(math.ceil(value / 100.0)) * 100

# --- Current Scenario ---
current_revenue = current_price * current_volume
current_cogs = cost_per_test * current_volume
current_opex = 0.25 * current_revenue
current_profit = current_revenue - current_cogs - current_opex
current_margin = (current_profit / current_revenue) * 100

# --- Proposed Scenario ---
proposed_revenue = proposed_price * proposed_volume
proposed_cogs = cost_per_test * proposed_volume

# Opex increases slightly with higher test volume
volume_growth = (proposed_volume - current_volume) / current_volume
opex_increase_factor = 1 + (volume_growth * (volume_opex_adj / 100))
proposed_opex = 0.25 * proposed_revenue * opex_increase_factor

proposed_profit = proposed_revenue - proposed_cogs - proposed_opex
proposed_margin = (proposed_profit / proposed_revenue) * 100

# --- Round values ---
current_revenue = round_up(current_revenue)
current_cogs = round_up(current_cogs)
current_opex = round_up(current_opex)
current_profit = round_up(current_profit)

proposed_revenue = round_up(proposed_revenue)
proposed_cogs = round_up(proposed_cogs)
proposed_opex = round_up(proposed_opex)
proposed_profit = round_up(proposed_profit)

# --- Display Results ---
st.header("Performance Summary")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Performance")
    st.write(f"**Revenue:** ₦{current_revenue:,}")
    st.write(f"**COGS:** ₦{current_cogs:,}")
    st.write(f"**Opex (25%):** ₦{current_opex:,}")
    st.write(f"**Profit:** ₦{current_profit:,}")
    st.write(f"**Profit Margin:** {current_margin:.1f}%")

with col2:
    st.subheader("Proposed Performance")
    st.write(f"**Revenue:** ₦{proposed_revenue:,}")
    st.write(f"**COGS:** ₦{proposed_cogs:,}")
    st.write(f"**Opex (Adjusted):** ₦{proposed_opex:,}")
    st.write(f"**Profit:** ₦{proposed_profit:,}")
    st.write(f"**Profit Margin:** {proposed_margin:.1f}%")

# --- Comparison Summary ---
st.header("Impact Overview")
st.write(f"- Revenue change: ₦{round_up(proposed_revenue - current_revenue):,}")
st.write(f"- Profit change: ₦{round_up(proposed_profit - current_profit):,}")
st.write(f"- Margin difference: {(proposed_margin - current_margin):.1f}%")
st.write(f"- Opex increased by approximately {(opex_increase_factor - 1) * 100:.1f}% due to higher test volume.")
