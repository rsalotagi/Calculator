import streamlit as st


# ============================================================
# Calculation Functions
# ============================================================

def calculate_liquidation_price(
    entry_price,
    leverage,
    maintenance_margin_rate,
    side
):
    """
    Approximate isolated-margin liquidation price for a
    linear/vanilla contract.

    NOTE:
    This is an estimate. Delta Exchange's actual liquidation
    price is computed by its risk engine and may differ.
    """

    if side == "long":
        return entry_price * (
            1 - (1 / leverage) + maintenance_margin_rate
        )

    elif side == "short":
        return entry_price * (
            1 + (1 / leverage) - maintenance_margin_rate
        )

    else:
        raise ValueError("Side must be 'long' or 'short'")


def calculate_lots(
    capital,
    risk_percent,
    entry_price,
    stop_loss_price,
    fee_rate,
    contract_value,
    leverage
):
    """
    Calculates position size using two limits:

    1. Risk-based position size
    2. Leverage/margin-based position size

    Final position = minimum of the two.
    """

    price_diff = abs(entry_price - stop_loss_price)

    denominator = (
        price_diff
        + fee_rate * (entry_price + stop_loss_price)
    )

    if denominator <= 0:
        raise ValueError(
            "Invalid inputs: denominator must be greater than zero."
        )

    Q_risk = (
        capital * risk_percent
    ) / denominator

    Q_margin_max = (
        capital * leverage
    ) / entry_price

    Q_final = min(
        Q_risk,
        Q_margin_max
    )

    lots = int(
        Q_final / contract_value
    )

    return (
        Q_risk,
        Q_margin_max,
        Q_final,
        lots
    )


def calculate_rr_ratios(
    entry_price,
    stop_loss_price,
    targets
):
    """
    Calculates R:R ratio for each target.
    """

    risk = abs(
        entry_price - stop_loss_price
    )

    if risk <= 0:
        raise ValueError(
            "Risk distance must be greater than zero."
        )

    rr_results = {}

    for label, price in targets.items():

        if price is not None:
            reward = abs(
                price - entry_price
            )

            rr_results[label] = (
                reward / risk
            )

    return rr_results


# ============================================================
# Streamlit Configuration
# ============================================================

st.set_page_config(
    page_title="Delta Position & Risk Calculator",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# Header
# ============================================================

st.title("📊 Delta Position & Risk Calculator")

st.caption(
    "Risk-based position sizing • Leverage cap • "
    "Liquidation estimate • Risk:Reward"
)


# ============================================================
# Sidebar - Inputs
# ============================================================

with st.sidebar:

    st.header("Trade Parameters")

    capital = st.number_input(
        "Total Capital",
        min_value=0.01,
        value=1000.0,
        step=100.0,
        format="%.2f"
    )

    risk_percent_display = st.number_input(
        "Risk Percentage (%)",
        min_value=0.01,
        max_value=100.0,
        value=1.0,
        step=0.1,
        format="%.2f"
    )

    # Convert percentage to decimal
    risk_percent = (
        risk_percent_display / 100
    )

    entry_price = st.number_input(
        "Entry Price",
        min_value=0.00000001,
        value=100000.0,
        step=100.0,
        format="%.8f"
    )

    stop_loss_price = st.number_input(
        "Stop Loss Price",
        min_value=0.00000001,
        value=99500.0,
        step=100.0,
        format="%.8f"
    )

    fee_rate_display = st.number_input(
        "Commission Fee Rate (%)",
        min_value=0.0,
        value=0.05,
        step=0.01,
        format="%.4f"
    )

    # Convert percentage to decimal
    fee_rate = (
        fee_rate_display / 100
    )

    contract_value = st.number_input(
        "Contract Value per Lot",
        min_value=0.00000001,
        value=0.001,
        step=0.001,
        format="%.8f"
    )

    leverage = st.number_input(
        "Leverage (x)",
        min_value=0.1,
        value=50.0,
        step=1.0,
        format="%.1f"
    )

    side = st.radio(
        "Position Side",
        ["long", "short"],
        horizontal=True
    )

    st.header("Liquidation Parameters")

    maintenance_margin_display = st.number_input(
        "Maintenance Margin Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.25,
        step=0.05,
        format="%.4f",
        help="Example: enter 0.25 for 0.25%"
    )

    # Convert percentage to decimal
    maintenance_margin_rate = (
        maintenance_margin_display / 100
    )

    st.header("Target Prices")

    t1 = st.number_input(
        "Target T1",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.8f"
    )

    t2 = st.number_input(
        "Target T2",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.8f"
    )

    t3 = st.number_input(
        "Target T3",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.8f"
    )

    calculate_button = st.button(
        "🧮 Calculate",
        type="primary",
        use_container_width=True
    )


# ============================================================
# Calculation
# ============================================================

if calculate_button:

    try:

        # ----------------------------------------------------
        # Validate Inputs
        # ----------------------------------------------------

        if capital <= 0:
            raise ValueError(
                "Capital must be greater than zero."
            )

        if risk_percent <= 0:
            raise ValueError(
                "Risk percentage must be greater than zero."
            )

        if entry_price <= 0:
            raise ValueError(
                "Entry price must be greater than zero."
            )

        if stop_loss_price <= 0:
            raise ValueError(
                "Stop-loss price must be greater than zero."
            )

        if contract_value <= 0:
            raise ValueError(
                "Contract value must be greater than zero."
            )

        if leverage <= 0:
            raise ValueError(
                "Leverage must be greater than zero."
            )

        # ----------------------------------------------------
        # Basic Long / Short Validation
        # ----------------------------------------------------

        if (
            side == "long"
            and stop_loss_price >= entry_price
        ):
            st.warning(
                "For a LONG position, the stop-loss "
                "is normally below the entry price."
            )

        if (
            side == "short"
            and stop_loss_price <= entry_price
        ):
            st.warning(
                "For a SHORT position, the stop-loss "
                "is normally above the entry price."
            )

        # ----------------------------------------------------
        # Targets
        # ----------------------------------------------------

        targets = {

            "T1": (
                t1
                if t1 > 0
                else None
            ),

            "T2": (
                t2
                if t2 > 0
                else None
            ),

            "T3": (
                t3
                if t3 > 0
                else None
            )
        }

        # ====================================================
        # Position Sizing
        # ====================================================

        (
            Q_risk,
            Q_margin_max,
            Q_final,
            lots
        ) = calculate_lots(

            capital,
            risk_percent,
            entry_price,
            stop_loss_price,
            fee_rate,
            contract_value,
            leverage
        )

        # Actual position after whole-lot rounding
        actual_Q = (
            lots * contract_value
        )

        # Notional value
        notional = (
            actual_Q * entry_price
        )

        # Required margin
        margin_required = (
            notional / leverage
        )

        # Maximum allowed risk amount
        risk_amount = (
            capital * risk_percent
        )

        # Price distance between Entry and SL
        price_diff = abs(
            entry_price - stop_loss_price
        )

        # ====================================================
        # Fee / Loss Calculation
        # ====================================================

        # Entry + exit fee
        estimated_fees = (
            actual_Q
            * fee_rate
            * (
                entry_price
                + stop_loss_price
            )
        )

        # Loss from price movement
        estimated_sl_loss = (
            actual_Q
            * price_diff
        )

        # Total estimated loss including fees
        estimated_total_loss = (
            estimated_sl_loss
            + estimated_fees
        )

        # ====================================================
        # Liquidation Price
        # ====================================================

        liquidation_price = (
            calculate_liquidation_price(

                entry_price,
                leverage,
                maintenance_margin_rate,
                side
            )
        )

        # ====================================================
        # R:R
        # ====================================================

        rr_ratios = (
            calculate_rr_ratios(

                entry_price,
                stop_loss_price,
                targets
            )
        )

        # ====================================================
        # POSITION SIZING DISPLAY
        # ====================================================

        st.subheader(
            "📐 Position Sizing"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Risk Amount",
            f"{risk_amount:,.2f}"
        )

        col2.metric(
            "Risk-Based Max Q",
            f"{Q_risk:,.8f}"
        )

        col3.metric(
            "Margin-Based Max Q",
            f"{Q_margin_max:,.8f}"
        )

        col4.metric(
            "Final Q",
            f"{Q_final:,.8f}"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Maximum Lots",
            f"{lots:,}"
        )

        col2.metric(
            "Actual Position",
            f"{actual_Q:,.8f}"
        )

        col3.metric(
            "Notional Value",
            f"{notional:,.2f}"
        )

        col4.metric(
            "Margin Required",
            f"{margin_required:,.2f}"
        )

        # ----------------------------------------------------
        # Position Cap Explanation
        # ----------------------------------------------------

        if Q_risk <= Q_margin_max:

            st.success(
                "Position size is capped by your "
                "risk limit."
            )

        else:

            st.warning(
                "Position size is capped by your "
                "leverage/margin capacity."
            )

        if lots == 0:

            st.error(
                "Calculated lot size is 0. "
                "The allowed risk or margin capacity "
                "is too small for this trade."
            )

        # ====================================================
        # RISK BREAKDOWN
        # ====================================================

        st.subheader(
            "💰 Risk Breakdown"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "SL Price Distance",
            f"{price_diff:,.8f}"
        )

        col2.metric(
            "Estimated SL Loss",
            f"{estimated_sl_loss:,.2f}"
        )

        col3.metric(
            "Estimated Fees",
            f"{estimated_fees:,.2f}"
        )

        st.metric(
            "Estimated Total Loss at SL",
            f"{estimated_total_loss:,.2f}"
        )

        # ====================================================
        # LIQUIDATION
        # ====================================================

        st.subheader(
            "⚠️ Estimated Liquidation Price"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Side",
            side.upper()
        )

        col2.metric(
            "Estimated Liquidation",
            f"{liquidation_price:,.2f}"
        )

        col3.metric(
            "Maintenance Margin",
            f"{maintenance_margin_display:.4f}%"
        )

        st.warning(
            "This liquidation price is an estimate only. "
            "Delta Exchange's actual risk engine may calculate "
            "a different liquidation price."
        )

        # ----------------------------------------------------
        # SL vs Liquidation Warning
        # ----------------------------------------------------

        if (
            side == "long"
            and stop_loss_price <= liquidation_price
        ):

            st.error(
                "🚨 WARNING: Your stop-loss is at or below "
                "the estimated liquidation price. "
                "The position may be liquidated before "
                "the stop-loss executes."
            )

        elif (
            side == "short"
            and stop_loss_price >= liquidation_price
        ):

            st.error(
                "🚨 WARNING: Your stop-loss is at or above "
                "the estimated liquidation price. "
                "The position may be liquidated before "
                "the stop-loss executes."
            )

        else:

            st.success(
                "✅ Stop-loss is on the non-liquidation "
                "side of the estimated liquidation price."
            )

        # ====================================================
        # RISK : REWARD
        # ====================================================

        st.subheader(
            "🎯 Risk : Reward"
        )

        if rr_ratios:

            columns = st.columns(
                len(rr_ratios)
            )

            for column, (
                label,
                rr
            ) in zip(
                columns,
                rr_ratios.items()
            ):

                column.metric(
                    label,
                    f"1 : {rr:.2f}"
                )

            # Detailed table
            rr_table = []

            for label, rr in rr_ratios.items():

                target_price = (
                    targets[label]
                )

                reward_distance = abs(
                    target_price
                    - entry_price
                )

                rr_table.append({

                    "Target":
                        label,

                    "Target Price":
                        target_price,

                    "Risk Distance":
                        price_diff,

                    "Reward Distance":
                        reward_distance,

                    "R:R":
                        f"1:{rr:.2f}"
                })

            st.dataframe(
                rr_table,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No target prices provided. "
                "R:R calculation skipped."
            )

        # ====================================================
        # TRADE SUMMARY
        # ====================================================

        st.subheader(
            "📋 Trade Summary"
        )

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.write(
                f"**Side:** {side.upper()}"
            )

            st.write(
                f"**Entry:** {entry_price:,.8f}"
            )

            st.write(
                f"**Stop Loss:** {stop_loss_price:,.8f}"
            )

            st.write(
                f"**Leverage:** {leverage:g}x"
            )

            st.write(
                f"**Risk:** {risk_percent_display:.2f}%"
            )

        with summary_col2:

            st.write(
                f"**Maximum Lots:** {lots:,}"
            )

            st.write(
                f"**Actual Position:** {actual_Q:,.8f}"
            )

            st.write(
                f"**Notional:** {notional:,.2f}"
            )

            st.write(
                f"**Margin:** {margin_required:,.2f}"
            )

            st.write(
                f"**Estimated Liquidation:** "
                f"{liquidation_price:,.2f}"
            )

    except ValueError as e:

        st.error(
            f"Input Error: {e}"
        )

    except Exception as e:

        st.error(
            f"Unexpected error: {e}"
        )

else:

    st.info(
        "Enter your trade parameters in the left panel "
        "and click **Calculate**."
    )


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "The formulas are based on the Python script provided. "
    "Liquidation price is an estimate and should not be "
    "treated as Delta Exchange's exact liquidation price."
)
