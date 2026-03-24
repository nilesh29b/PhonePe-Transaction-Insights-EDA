# ============================================================
# PhonePe Pulse — Streamlit Dashboard
# Purpose: Interactive dashboard to explore PhonePe
#          transaction, user, and insurance data
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text

# ============================================================
# PAGE CONFIGURATION
# Must be the first Streamlit command in the script
# ============================================================

st.set_page_config(
    page_title="PhonePe Pulse Dashboard",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# Purpose: Style the dashboard to match PhonePe's brand
#          colors — purple and white
# ============================================================

st.markdown("""
    <style>
    .main {background-color: #0d0d0d;}
    .stMetric {
        background-color: #1a1a2e;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #6c35de;
    }
    .stMetric label {color: #a78bfa !important;}
    .stMetric .metric-value {color: #ffffff !important;}
    div[data-testid="stSidebarContent"] {
        background-color: #1a1a2e;
    }
    h1, h2, h3 {color: #a78bfa;}
    .stSelectbox label {color: #a78bfa;}
    </style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE CONNECTION
# We use st.cache_resource so the connection is created
# once and reused across all user interactions.
# Without caching, a new connection would be created
# every time the user changes a filter -- very slow.
# ============================================================

@st.cache_resource
def get_engine():
    DB_USER = "postgres"
    DB_PASSWORD = "1234"  # ← change this
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "phonepe_pulse"
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

engine = get_engine()

# ============================================================
# DATA LOADING FUNCTIONS
# We use st.cache_data so query results are cached.
# This means when a user changes a filter, only the
# affected queries re-run -- not all queries at once.
# The underscore in _engine tells Streamlit not to
# try to hash the engine object.
# ============================================================

@st.cache_data
def load_years(_engine):
    with _engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT year FROM aggregated_transaction
            ORDER BY year
        """))
        return [row[0] for row in result]

@st.cache_data
def load_states(_engine):
    with _engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT state FROM aggregated_transaction
            WHERE state != 'india'
            ORDER BY state
        """))
        return [row[0] for row in result]

@st.cache_data
def load_transaction_summary(_engine, year_filter, quarter_filter):
    year_clause = f"AND year = {year_filter}" if year_filter != 'All' else ""
    quarter_clause = f"AND quarter = {quarter_filter}" \
        if quarter_filter != 'All' else ""
    with _engine.connect() as conn:
        return pd.read_sql(text(f"""
            SELECT
                SUM(transaction_count) AS total_transactions,
                ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount,
                COUNT(DISTINCT state) AS active_states
            FROM aggregated_transaction
            WHERE state != 'india'
            {year_clause}
            {quarter_clause}
        """), conn)

@st.cache_data
def load_category_data(_engine, year_filter, quarter_filter):
    year_clause = f"AND year = {year_filter}" if year_filter != 'All' else ""
    quarter_clause = f"AND quarter = {quarter_filter}" \
        if quarter_filter != 'All' else ""
    with _engine.connect() as conn:
        return pd.read_sql(text(f"""
            SELECT
                transaction_type,
                SUM(transaction_count) AS total_transactions,
                ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
            FROM aggregated_transaction
            WHERE state != 'india'
            {year_clause}
            {quarter_clause}
            GROUP BY transaction_type
            ORDER BY total_transactions DESC
        """), conn)

@st.cache_data
def load_state_data(_engine, year_filter, quarter_filter):
    year_clause = f"AND year = {year_filter}" if year_filter != 'All' else ""
    quarter_clause = f"AND quarter = {quarter_filter}" \
        if quarter_filter != 'All' else ""
    with _engine.connect() as conn:
        return pd.read_sql(text(f"""
            SELECT
                state,
                SUM(transaction_count) AS total_transactions,
                ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
            FROM aggregated_transaction
            WHERE state != 'india'
            {year_clause}
            {quarter_clause}
            GROUP BY state
            ORDER BY total_transactions DESC
        """), conn)

@st.cache_data
def load_yoy_data(_engine):
    with _engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                year,
                SUM(transaction_count) AS total_transactions,
                ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
            FROM aggregated_transaction
            WHERE state != 'india'
            GROUP BY year
            ORDER BY year
        """), conn)

@st.cache_data
def load_district_data(_engine, state_filter):
    state_clause = f"AND state = '{state_filter}'" \
        if state_filter != 'All' else ""
    with _engine.connect() as conn:
        return pd.read_sql(text(f"""
            SELECT
                state,
                district,
                SUM(transaction_count) AS total_transactions,
                ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
            FROM map_transaction
            WHERE 1=1
            {state_clause}
            GROUP BY state, district
            ORDER BY total_transactions DESC
            LIMIT 15
        """), conn)

@st.cache_data
def load_device_data(_engine):
    with _engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                device_brand,
                SUM(device_count) AS total_users,
                ROUND(
                    100.0 * SUM(device_count) /
                    SUM(SUM(device_count)) OVER(), 2
                ) AS percentage_share
            FROM aggregated_user
            WHERE state != 'india'
            GROUP BY device_brand
            ORDER BY total_users DESC
        """), conn)

@st.cache_data
def load_engagement_data(_engine):
    with _engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                state,
                SUM(registered_users) AS total_registered,
                SUM(app_opens) AS total_app_opens,
                ROUND(
                    (SUM(app_opens)::NUMERIC /
                    NULLIF(SUM(registered_users), 0)),
                    2
                ) AS avg_opens_per_user
            FROM aggregated_user
            WHERE state != 'india'
            GROUP BY state
            ORDER BY avg_opens_per_user DESC
        """), conn)

@st.cache_data
def load_insurance_data(_engine, year_filter):
    year_clause = f"AND year = {year_filter}" if year_filter != 'All' else ""
    with _engine.connect() as conn:
        return pd.read_sql(text(f"""
            SELECT
                state,
                SUM(transaction_count) AS total_insurance,
                ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
            FROM aggregated_insurance
            WHERE state != 'india'
            {year_clause}
            GROUP BY state
            ORDER BY total_insurance DESC
            LIMIT 10
        """), conn)

@st.cache_data
def load_insurance_yoy(_engine):
    with _engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                year,
                SUM(transaction_count) AS total_insurance,
                ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
            FROM aggregated_insurance
            WHERE state != 'india'
            GROUP BY year
            ORDER BY year
        """), conn)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.image(
    "dashboard/assets/phonepe_logo.png",
    width=180
)

st.sidebar.markdown("## 📊 Dashboard Filters")

# ============================================================
# CLEAR FILTERS LOGIC
# Simplest reliable approach -- store selections in
# session state manually, reset by setting to 0 index
# before widgets are rendered
# ============================================================

# Set defaults on first load
for key, default in [
    ('sel_year', 'All'),
    ('sel_quarter', 'All'),
    ('sel_state', 'All')
]:
    if key not in st.session_state:
        st.session_state[key] = default

years = ['All'] + load_years(engine)
quarters = ['All', 1, 2, 3, 4]
states = ['All'] + load_states(engine)

selected_year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=years.index(st.session_state['sel_year'])
)
st.session_state['sel_year'] = selected_year

selected_quarter = st.sidebar.selectbox(
    "Select Quarter",
    quarters,
    index=quarters.index(st.session_state['sel_quarter'])
)
st.session_state['sel_quarter'] = selected_quarter

state_index = states.index(st.session_state['sel_state']) \
    if st.session_state['sel_state'] in states else 0

selected_state = st.sidebar.selectbox(
    "Select State",
    states,
    index=state_index
)
st.session_state['sel_state'] = selected_state

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Clear All Filters"):
    st.session_state['sel_year'] = 'All'
    st.session_state['sel_quarter'] = 'All'
    st.session_state['sel_state'] = 'All'
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Overview",
        "💳 Transaction Analysis",
        "👥 User & Device Analysis",
        "🗺️ District Deep Dive",
        "🛡️ Insurance Analysis"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data Source:** PhonePe Pulse GitHub  \n"
    "**Last Updated:** 2024  \n"
    "**Total Records:** 116,749"
)

# ============================================================
# PAGE 1 - OVERVIEW
# ============================================================

if page == "🏠 Overview":
    st.title("💜 PhonePe Pulse Dashboard")
    st.markdown(
        "### India's Digital Payment Landscape — "
        "2018 to 2024"
    )
    st.markdown("---")

    # Key metrics row
    summary = load_transaction_summary(
        engine, selected_year, selected_quarter
    )
    ins_yoy = load_insurance_yoy(engine)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_trans = summary['total_transactions'].iloc[0]
        st.metric(
            "Total Transactions",
            f"{total_trans/1e9:.1f}B",
            delta="↑ 54.5% YoY (2024)"
        )
    with col2:
        total_amt = summary['total_amount'].iloc[0]
        st.metric(
            "Total Transaction Value",
            f"₹{total_amt/1e12:.1f}T",
            delta="↑ 37.2% YoY (2024)"
        )
    with col3:
        st.metric(
            "States Covered",
            "36",
            delta="All Indian States & UTs"
        )
    with col4:
        total_ins = ins_yoy['total_insurance'].sum()
        st.metric(
            "Insurance Transactions",
            f"{total_ins/1e6:.1f}M",
            delta="↑ 27.1% YoY (2024)"
        )

    st.markdown("---")

    # Two charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Transaction Growth 2018—2024")
        yoy_data = load_yoy_data(engine)
        yoy_data['transactions_billion'] = \
            yoy_data['total_transactions'] / 1e9
        fig = px.bar(
            yoy_data,
            x='year',
            y='transactions_billion',
            title='Year over Year Transaction Volume',
            color='transactions_billion',
            color_continuous_scale='Purples',
            text=yoy_data['transactions_billion'].round(1)
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            template='plotly_dark',
            height=400,
            showlegend=False,
            coloraxis_showscale=False
        )
        fig.update_yaxes(title_text='Transactions (Billions)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Payment Category Distribution")
        cat_data = load_category_data(
            engine, selected_year, selected_quarter
        )
        fig = px.pie(
            cat_data,
            values='total_transactions',
            names='transaction_type',
            title='Transaction Count by Category',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig.update_layout(
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 2 - TRANSACTION ANALYSIS
# ============================================================

elif page == "💳 Transaction Analysis":
    st.title("💳 Transaction Analysis")
    st.markdown(
        f"**Filters Applied:** Year: {selected_year} | "
        f"Quarter: {selected_quarter}"
    )
    st.markdown("---")

    # Top states chart
    st.subheader("Top 10 States by Transaction Volume")
    state_data = load_state_data(
        engine, selected_year, selected_quarter
    )
    state_data['transactions_billion'] = \
        state_data['total_transactions'] / 1e9
    state_data['state_clean'] = state_data['state'].str.replace(
        '-', ' ').str.title()
    state_data['amount_trillion'] = state_data['total_amount'] / 1e12

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            state_data.head(10).sort_values(
                'transactions_billion', ascending=True
            ),
            x='transactions_billion',
            y='state_clean',
            orientation='h',
            title='Top 10 States — Transaction Count',
            color='transactions_billion',
            color_continuous_scale='Purples',
            text=state_data.head(10).sort_values(
                'transactions_billion',
                ascending=True
            )['transactions_billion'].round(1)
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            template='plotly_dark',
            height=450,
            coloraxis_showscale=False
        )
        fig.update_xaxes(title_text='Transactions (Billions)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            state_data.head(10).sort_values(
                'amount_trillion', ascending=True
            ),
            x='amount_trillion',
            y='state_clean',
            orientation='h',
            title='Top 10 States — Transaction Value',
            color='amount_trillion',
            color_continuous_scale='Purples',
            text=state_data.head(10).sort_values(
                'amount_trillion',
                ascending=True
            )['amount_trillion'].round(1)
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            template='plotly_dark',
            height=450,
            coloraxis_showscale=False
        )
        fig.update_xaxes(title_text='Amount (₹ Trillion)')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Payment Category Breakdown")
    cat_data = load_category_data(
        engine, selected_year, selected_quarter
    )
    cat_data['amount_trillion'] = cat_data['total_amount'] / 1e12
    cat_data['transactions_billion'] = \
        cat_data['total_transactions'] / 1e9

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            'Transaction Count by Category',
            'Transaction Value by Category (₹T)'
        )
    )
    colors = px.colors.sequential.Purples_r[:5]

    fig.add_trace(
        go.Bar(
            x=cat_data['transaction_type'],
            y=cat_data['transactions_billion'],
            marker_color=colors,
            text=cat_data['transactions_billion'].round(1),
            textposition='outside',
            showlegend=False
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=cat_data['transaction_type'],
            y=cat_data['amount_trillion'],
            marker_color=colors,
            text=cat_data['amount_trillion'].round(1),
            textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )
    fig.update_layout(
        template='plotly_dark',
        height=400
    )
    fig.update_xaxes(tickangle=15)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 3 - USER & DEVICE ANALYSIS
# ============================================================

elif page == "👥 User & Device Analysis":
    st.title("👥 User & Device Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Device Brand Market Share")
        device_data = load_device_data(engine)
        fig = px.treemap(
            device_data,
            path=['device_brand'],
            values='total_users',
            color='percentage_share',
            color_continuous_scale='Purples',
            title='User Distribution by Device Brand'
        )
        fig.update_layout(
            template='plotly_dark',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("User Engagement by State")
        eng_data = load_engagement_data(engine)
        eng_data['state_clean'] = eng_data['state'].str.replace(
            '-', ' ').str.title()
        eng_sorted = eng_data.sort_values(
            'avg_opens_per_user', ascending=True
        ).tail(15)

        fig = px.bar(
            eng_sorted,
            x='avg_opens_per_user',
            y='state_clean',
            orientation='h',
            title='Top 15 States — App Opens per User',
            color='avg_opens_per_user',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            template='plotly_dark',
            height=450,
            coloraxis_showscale=False
        )
        fig.update_xaxes(title_text='Opens per User')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Registered Users vs App Opens")
    eng_data['registered_million'] = \
        eng_data['total_registered'] / 1e6
    eng_data['opens_billion'] = \
        eng_data['total_app_opens'] / 1e9

    fig = px.scatter(
        eng_data,
        x='registered_million',
        y='opens_billion',
        text='state_clean',
        size='registered_million',
        color='avg_opens_per_user',
        color_continuous_scale='Purples',
        title='Registered Users vs App Opens by State'
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(
        template='plotly_dark',
        height=500
    )
    fig.update_xaxes(title_text='Registered Users (Millions)')
    fig.update_yaxes(title_text='Total App Opens (Billions)')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 4 - DISTRICT DEEP DIVE
# ============================================================

elif page == "🗺️ District Deep Dive":
    st.title("🗺️ District Deep Dive")
    st.markdown(
        f"**State Filter:** {selected_state}"
    )
    st.markdown("---")

    district_data = load_district_data(engine, selected_state)
    district_data['transactions_billion'] = \
        district_data['total_transactions'] / 1e9
    district_data['amount_trillion'] = \
        district_data['total_amount'] / 1e12
    district_data['state_clean'] = district_data['state'].str.replace(
        '-', ' ').str.title()
    district_data['district_clean'] = \
        district_data['district'].str.replace(
            '-', ' ').str.title()

    st.subheader(
        f"Top 15 Districts — "
        f"{'All States' if selected_state == 'All' else selected_state}"
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            district_data.sort_values(
                'transactions_billion', ascending=True
            ),
            x='transactions_billion',
            y='district_clean',
            orientation='h',
            color='state_clean',
            title='Transaction Count by District',
            text=district_data.sort_values(
                'transactions_billion',
                ascending=True
            )['transactions_billion'].round(1)
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            template='plotly_dark',
            height=550
        )
        fig.update_xaxes(title_text='Transactions (Billions)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            district_data.sort_values(
                'amount_trillion', ascending=True
            ),
            x='amount_trillion',
            y='district_clean',
            orientation='h',
            color='state_clean',
            title='Transaction Value by District',
            text=district_data.sort_values(
                'amount_trillion',
                ascending=True
            )['amount_trillion'].round(1)
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            template='plotly_dark',
            height=550
        )
        fig.update_xaxes(title_text='Amount (₹ Trillion)')
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 5 - INSURANCE ANALYSIS
# ============================================================

elif page == "🛡️ Insurance Analysis":
    st.title("🛡️ Insurance Analysis")
    st.markdown(
        f"**Year Filter:** {selected_year}"
    )
    st.markdown(
        "> ⚠️ Insurance data starts from 2020 Q2. "
        "2020 figures are understated due to missing Q1 data."
    )
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Insurance Growth 2020—2024")
        ins_yoy = load_insurance_yoy(engine)
        ins_yoy['amount_billion'] = ins_yoy['total_amount'] / 1e9

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=ins_yoy['year'],
                y=ins_yoy['total_insurance'],
                name='Transaction Count',
                marker_color='#6c35de',
                text=ins_yoy['total_insurance'].apply(
                    lambda x: f'{x/1e6:.1f}M'
                ),
                textposition='outside'
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=ins_yoy['year'],
                y=ins_yoy['amount_billion'],
                name='Amount (₹B)',
                mode='lines+markers',
                line=dict(color='#a78bfa', width=3),
                marker=dict(size=10)
            ),
            secondary_y=True
        )
        fig.update_layout(
            template='plotly_dark',
            height=400,
            title='Insurance Transactions and Value Growth'
        )
        fig.update_yaxes(
            title_text='Transaction Count',
            secondary_y=False
        )
        fig.update_yaxes(
            title_text='Amount (₹ Billion)',
            secondary_y=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 States by Insurance")
        ins_data = load_insurance_data(engine, selected_year)
        ins_data['state_clean'] = ins_data['state'].str.replace(
            '-', ' ').str.title()
        ins_data['amount_billion'] = ins_data['total_amount'] / 1e9

        fig = px.bar(
            ins_data.sort_values('total_insurance', ascending=True),
            x='total_insurance',
            y='state_clean',
            orientation='h',
            color='amount_billion',
            color_continuous_scale='Purples',
            title='Top 10 States — Insurance Transactions',
            text=ins_data.sort_values(
                'total_insurance',
                ascending=True
            )['total_insurance'].apply(lambda x: f'{x/1e6:.2f}M')
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            template='plotly_dark',
            height=400,
            coloraxis_colorbar=dict(title='Amount (₹B)')
        )
        st.plotly_chart(fig, use_container_width=True)
