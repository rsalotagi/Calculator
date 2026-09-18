import streamlit as st

st.set_page_config(
    page_title="BTC/ETH Position Size Calculator",
    page_icon="📊",
    layout="centered"
)

st.title("📊 BTC/ETH Position Size Calculator")
st.caption("Risk-based lot calculator using your original calculation logic")

def calculate_lots(capital, risk_percent, entry_price, stop_loss_price, fee_rate, contract_value):
    price_diff = abs(entry_price - stop_loss_price)
    denominator = price_diff + fee_rate * (entry_price + stop_loss_price)

    if denominator <= 0:
        raise ValueError("Invalid inputs: denominator must be greater than zero.")

    Q = (capital * risk_percent) / denominator
    lots = int(Q / contract_value)

    return Q, lots

st.subheader("Trade Parameters")

capital = st.number_input(
    "Total Capital (C)",
    min_value=0.01,
    value=1000.0,
    step=100.0,
    format="%.2f"
)

risk_percent_input = st.number_input(
    "Risk Percentage (%)",
    min_value=0.01,
    value=1.0,
    step=0.1,
    format="%.2f"
)

entry_price = st.number_input(
    "Entry Price (P_entry)",
    min_value=0.00000001,
    value=100000.0,
    step=100.0,
    format="%.8f"
)

stop_loss_price = st.number_input(
    "Stop Loss Price (P_sl)",
    min_value=0.00000001,
    value=99500.0,
    step=100.0,
    format="%.8f"
)

fee_rate_percent = st.number_input(
    "Commission Fee Rate (%)",
    min_value=0.0,
    value=0.05,
    step=0.01,
    format="%.4f"
)

contract_value = st.number_input(
    "Contract Value per Lot",
    min_value=0.00000001,
    value=0.001,
    step=0.001,
    format="%.8f"
)

calculate = st.button("🧮 Calculate", type="primary", use_container_width=True)

if calculate:
    try:
        if capital <= 0 or risk_percent_input <= 0 or entry_price <= 0 or contract_value <= 0:
            raise ValueError(
                "Capital, risk percentage, entry price, and contract value must be positive."
            )

        if stop_loss_price <= 0:
            raise ValueError("Stop-loss price must be positive.")

        fee_rate = fee_rate_percent / 100
        risk_percent = risk_percent_input / 100

        Q, lots = calculate_lots(
            capital,
            risk_percent,
            entry_price,
            stop_loss_price,
            fee_rate,
            contract_value
        )

        actual_Q = lots * contract_value
        risk_amount = capital * risk_percent
        price_diff = abs(entry_price - stop_loss_price)

        # Same fee model used in the original formula:
        # fee on entry + exit notional.
        estimated_fees = actual_Q * fee_rate * (entry_price + stop_loss_price)
        stop_loss_price_loss = actual_Q * price_diff
        total_risk = stop_loss_price_loss + estimated_fees

        st.divider()
        st.subheader("📈 Result")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Risk Amount", f"{risk_amount:,.8f}")
            st.metric("Calculated Position Size", f"{Q:,.8f}")
            st.metric("Maximum Lots", f"{lots:,}")

        with col2:
            st.metric("Actual Position Size", f"{actual_Q:,.8f}")
            st.metric("SL Price Distance", f"{price_diff:,.8f}")
            st.metric("Estimated Fees", f"{estimated_fees:,.8f}")

        st.divider()
        st.subheader("💰 Risk Breakdown")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Loss at SL", f"{stop_loss_price_loss:,.8f}")

        with c2:
            st.metric("Fees", f"{estimated_fees:,.8f}")

        with c3:
            st.metric("Total Risk", f"{total_risk:,.8f}")

        st.info(
            f"Your maximum calculated position is **{lots:,} lots**, "
            f"representing **{actual_Q:,.8f} units**."
        )

        if lots == 0:
            st.warning(
                "Calculated lot size is 0. The allowed risk may be too small "
                "for the stop-loss distance and fees."
            )

    except ValueError as e:
        st.error(f"Input Error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

st.divider()
st.caption(
    "Calculation follows the Python logic provided by you. "
    "Verify the fee rate and contract value against the specific Delta Exchange contract before live trading."
)
