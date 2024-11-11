from datetime import datetime

import plotly.graph_objs as go
import streamlit as st
import yfinance as yf
from dateutil.relativedelta import relativedelta

# Configure Streamlit page settings for white mode
st.set_page_config(
    page_title="ETF Analysis Dashboard",
    page_icon="📈",
    layout="wide",
)

# Custom CSS
st.markdown(
    """
    <style>
        .stApp {
            background-color: white;
        }
        .st-emotion-cache-16txtl3 h1 {
            padding-top: 0rem;
        }
        .st-emotion-cache-16txtl3 h2 {
            padding-top: 0rem;
        }
        [data-testid="column"] {
            padding: 0 20px;
        }
        [data-testid="column"]:first-child {
            padding-left: 0;
            padding-right: 20px;
        }
        [data-testid="column"]:last-child {
            padding-right: 0;
            padding-left: 20px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("The 12% Solution")

# Define the ticker symbols
equity_tickers = ["SPY", "QQQ", "IWM", "MDY", "SHY"]
bond_tickers = ["TLT", "JNK"]
all_tickers = equity_tickers + bond_tickers

colors_dict = {
    "SPY": "#0000ff",  # blue
    "QQQ": "#2ca02c",  # green
    "IWM": "#ff7f0e",  # orange
    "MDY": "#75E6DA",  # purple
    "SHY": "#1c1a1a",  # brown
    "TLT": "#81B622",  # pink
    "JNK": "#7f7f7f",  # gray
}

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
current_month = months[datetime.now().month - 1]

# Move date selection to sidebar
with st.sidebar:
    st.header("Date Selection")
    selected_month = st.selectbox(
        "Select Month", months, index=months.index(current_month)
    )
    selected_year = st.number_input(
        "Select Year",
        min_value=datetime.now().year - 10,
        max_value=datetime.now().year,
        value=datetime.now().year,
    )

selected_month_integer = months.index(selected_month) + 1

# Calculate dates
end_date = datetime(selected_year, selected_month_integer, 1) - relativedelta(days=1)
start_date_dt = end_date - relativedelta(days=90)
start_date = start_date_dt.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")
interval = "1d"

# Fetch data for both equity and bond ETFs
all_data = yf.download(
    all_tickers, start=start_date, end=end_date_str, interval=interval
)["Adj Close"]


equity_data = all_data[equity_tickers]
bond_data = all_data[bond_tickers]

# Display date range in sidebar
num_days = len(all_data)
with st.sidebar:
    st.write(f"From {start_date} to {end_date_str}")
    st.write(f"**Open market days**: {num_days} days")

# Create main columns for equity and bond analysis
main_col1, dummy, main_col2 = st.columns([0.4, 0.075, 0.4])

# Equity ETFs Column
with main_col1:
    st.header("Equity ETFs")

    # Calculate percentage changes for equity ETFs
    equity_pct_change = (equity_data / equity_data.iloc[0] - 1) * 100
    equity_pct_change["0%"] = 0
    equity_tickers_plot = equity_tickers + ["0%"]

    # Create equity plot
    fig_equity = go.Figure()
    for ticker in equity_tickers:
        fig_equity.add_trace(
            go.Scatter(
                x=equity_pct_change.index,
                y=equity_pct_change[ticker],
                mode="lines",
                name=ticker,
                line=dict(color=colors_dict[ticker]),
            )
        )
        # For the "0%" line specifically, add these parameters to go.Scatter:
    fig_equity.add_trace(
        go.Scatter(
            x=equity_pct_change.index,
            y=equity_pct_change["0%"],
            mode="lines",
            name="0%",
            line=dict(color="red", dash="dash"),  # This makes it red and dotted
            # opacity=0.5,  # Optional: makes it slightly transparent
        )
    )
    fig_equity.update_layout(
        title=f"%Change of Equity ETFs ({num_days} days lookback window)",
        xaxis_title="Date",
        yaxis_title="%",
        template="plotly_white",
        hovermode="x unified",
        legend_title="Ticker",
    )
    st.plotly_chart(fig_equity)

    # Calculate and display equity recommendation
    last_row_changes_equity = equity_pct_change.iloc[-1].drop("0%")
    max_ticker_equity = last_row_changes_equity.idxmax()
    max_change_equity = last_row_changes_equity[max_ticker_equity]
    result_equity = "Cash" if max_change_equity < 0 else max_ticker_equity
    if max_change_equity < 0:
        st.write("Consider converting to **Cash**")
    else:
        st.write(f"Buy: **{max_ticker_equity}** (Change: {max_change_equity:.2f}%)")

# Bond ETFs Column
with main_col2:
    st.header("Bond ETFs")

    # Calculate percentage changes for bond ETFs
    bond_pct_change = (bond_data / bond_data.iloc[0] - 1) * 100
    bond_pct_change["0%"] = 0

    # Create bond plot
    fig_bonds = go.Figure()
    for ticker in bond_tickers:
        fig_bonds.add_trace(
            go.Scatter(
                x=bond_pct_change.index,
                y=bond_pct_change[ticker],
                mode="lines",
                name=ticker,
                line=dict(color=colors_dict[ticker]),
            )
        )

    fig_bonds.add_trace(
        go.Scatter(
            x=bond_pct_change.index,
            y=bond_pct_change["0%"],
            mode="lines",
            name="0%",
            line=dict(color="red", dash="dash"),  # This makes it red and dotted
            # opacity=0.5,  # Optional: makes it slightly transparent
        )
    )

    fig_bonds.update_layout(
        title=f"%Change of Bond ETFs ({num_days} days lookback window)",
        xaxis_title="Date",
        yaxis_title="%",
        template="plotly_white",
        hovermode="x unified",
        legend_title="Ticker Symbols",
    )
    st.plotly_chart(fig_bonds)

    # Calculate and display bond recommendation
    last_row_changes_bonds = bond_pct_change.iloc[-1].drop("0%")
    max_ticker_bonds = last_row_changes_bonds.idxmax()
    max_change_bonds = last_row_changes_bonds[max_ticker_bonds]
    st.write(f"Buy: **{max_ticker_bonds}** (Change: {max_change_bonds:.2f}%)")
