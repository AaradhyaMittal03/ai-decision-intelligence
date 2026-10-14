
"""Professional dashboard for real-time decision intelligence."""

import pandas as pd
import plotly.express as px
import streamlit as st

from decision_intelligence.streaming.database import get_connection


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Decision Intelligence | Control Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# PROFESSIONAL STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: #F4F7FB;
        color: #17233D;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263247;
    }

    [data-testid="stSidebar"] * {
        color: #E5EAF4 !important;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(120deg, #101B35, #243D70);
        padding: 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px rgba(26, 44, 83, 0.12);
    }

    .hero h1 {
        color: white;
        font-size: 34px;
        font-weight: 800;
        margin: 8px 0;
    }

    .hero p {
        color: #D1DDF4;
        font-size: 14px;
        margin-bottom: 0;
    }

    .eyebrow {
        color: #8EB7FF;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .section-title {
        color: #17233D;
        font-size: 20px;
        font-weight: 800;
        margin-top: 22px;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #71809B;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .metric-card {
        background: #FFFFFF;
        padding: 21px;
        border: 1px solid #E4EAF3;
        border-radius: 16px;
        min-height: 125px;
        box-shadow: 0 5px 18px rgba(20, 35, 65, 0.035);
    }

    .metric-label {
        color: #71809B;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .metric-value {
        color: #17233D;
        font-size: 31px;
        font-weight: 800;
        line-height: 1.2;
    }

    .metric-note {
        color: #8996AA;
        font-size: 11px;
        margin-top: 8px;
    }

    .panel {
        background: white;
        border: 1px solid #E4EAF3;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 18px;
    }

    .status-pill {
        display: inline-block;
        background: #DDF8E9;
        color: #087443;
        padding: 7px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
    }

    .status-warning {
        background: #FFF0D9;
        color: #9A5A00;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #E4EAF3;
        border-radius: 12px;
        overflow: hidden;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATABASE QUERIES
# --------------------------------------------------


def load_dashboard_data(start_date=None, end_date=None):
    """Fetch dashboard metrics and event details from PostgreSQL."""

    
    date_filter = ""
    query_params = {}

    if start_date is not None:
        date_filter += " AND event_timestamp >= %(start_datetime)s"
        query_params["start_datetime"] = pd.Timestamp(start_date).tz_localize(
            "Asia/Kolkata"
        )

    if end_date is not None:
        date_filter += " AND event_timestamp < %(end_datetime)s"
        query_params["end_datetime"] = (
            pd.Timestamp(end_date) + pd.Timedelta(days=1)
        ).tz_localize("Asia/Kolkata")


    
    queries = {
        "summary": f"""
            SELECT
                COUNT(*) AS total_events,
                COUNT(DISTINCT event_id) AS unique_events,
                COUNT(*) FILTER (
                    WHERE event_type = 'purchase'
                ) AS purchases,
                COALESCE(
                    SUM(amount) FILTER (
                        WHERE event_type = 'purchase'
                    ), 0
                ) AS purchase_value,
                COUNT(DISTINCT user_id) AS unique_users,
                COUNT(*) FILTER (
                    WHERE event_timestamp >= NOW() - INTERVAL '24 hours'
                ) AS events_24h
            FROM business_events
            WHERE event_timestamp >= %(start_datetime)s
              AND event_timestamp < %(end_datetime)s
        """,
        "event_types": f"""
            SELECT event_type, COUNT(*) AS total
            FROM business_events
            WHERE event_timestamp >= %(start_datetime)s
              AND event_timestamp < %(end_datetime)s
            GROUP BY event_type
            ORDER BY total DESC
        """,
        "rejection_summary": """
            SELECT
                COUNT(*) AS rejected_events,
                COUNT(*) FILTER (
                    WHERE rejection_reasons IS NOT NULL
                ) AS with_reasons
            FROM rejected_events
            WHERE rejected_at >= %(start_datetime)s
              AND rejected_at < %(end_datetime)s
        """,
        "rejection_reasons": """
            SELECT reason, COUNT(*) AS total
            FROM rejected_events,
                 UNNEST(rejection_reasons) AS reason
            WHERE rejected_at >= %(start_datetime)s
              AND rejected_at < %(end_datetime)s
            GROUP BY reason
            ORDER BY total DESC
        """,
        "recent_events": """
            SELECT
                event_id,
                event_type,
                user_id,
                product_id,
                amount,
                event_timestamp
            FROM business_events
            WHERE event_timestamp >= %(start_datetime)s
              AND event_timestamp < %(end_datetime)s
            ORDER BY event_timestamp DESC
            LIMIT 15
        """,
        "recent_rejections": """
            SELECT
                id,
                event_payload,
                rejection_reasons,
                rejected_at
            FROM rejected_events
            WHERE rejected_at >= %(start_datetime)s
              AND rejected_at < %(end_datetime)s
            ORDER BY rejected_at DESC
            LIMIT 10
        """,
        "hourly": """
            SELECT
                DATE_TRUNC('hour', event_timestamp) AS hour,
                COUNT(*) AS total
            FROM business_events
            WHERE event_timestamp >= %(start_datetime)s
              AND event_timestamp < %(end_datetime)s
            GROUP BY hour
            ORDER BY hour
        """,
    }


   
    results = {}

    with get_connection() as connection:
        for name, query in queries.items():
            results[name] = pd.read_sql_query(
                query,
                connection,
                params=query_params if query_params else None,
            )

    return results



# --------------------------------------------------
# REUSABLE COMPONENTS
# --------------------------------------------------

def metric_card(label, value, note):
    """Display one KPI card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title, subtitle):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, horizontal=False):
    """Apply readable styling to all Plotly charts."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, sans-serif",
            color="#475569",
            size=12,
        ),
        margin=dict(l=20, r=25, t=25, b=20),
        showlegend=False,
        xaxis=dict(
            title_font=dict(color="#334155", size=12),
            tickfont=dict(color="#475569", size=11),
            showgrid=not horizontal,
            gridcolor="#E2E8F0",
            zeroline=False,
            showline=True,
            linecolor="#CBD5E1",
        ),
        yaxis=dict(
            title_font=dict(color="#334155", size=12),
            tickfont=dict(color="#475569", size=11),
            showgrid=horizontal,
            gridcolor="#E2E8F0",
            zeroline=False,
            showline=False,
        ),
    )
    return fig



# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## ◈ Decision Intelligence")
    st.caption("REAL-TIME ANALYTICS PLATFORM")
    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Executive Overview",
            "Event Monitoring",
            "Data Quality",
        ],
    )

    st.divider()
    st.markdown("**DATA SOURCE**")
    st.caption("PostgreSQL · Kafka event pipeline")
    st.caption("Data is queried live from the database.")

    if st.button("↻ Refresh dashboard", use_container_width=True):
        st.rerun()

    st.divider()
    st.caption("AI Decision Intelligence Platform")
    st.caption("Built with Python · Streamlit · PostgreSQL")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AI-POWERED ANALYTICS PLATFORM</div>
        <h1>Decision Intelligence</h1>
        <p>
            Real-time event monitoring, data quality analytics,
            and operational visibility in one workspace.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load live database data.

# Select a date range for dashboard analysis.
st.subheader("📅 Filter by Date")

today = pd.Timestamp.now(tz="Asia/Kolkata").date()
default_start = today - pd.Timedelta(days=6)

date_col1, date_col2 = st.columns(2)

with date_col1:
    start_date = st.date_input(
        "Start date",
        value=default_start,
        max_value=today,
        key="dashboard_start_date",
    )

with date_col2:
    end_date = st.date_input(
        "End date",
        value=today,
        min_value=start_date,
        max_value=today,
        key="dashboard_end_date",
    )

if start_date > end_date:
    st.error("Start date must be on or before the end date.")
    st.stop()

# Load dashboard data for the selected date range.
try:
    data = load_dashboard_data(
        start_date=start_date,
        end_date=end_date,
    )


except Exception as error:
    import traceback

    st.error("Unable to load dashboard data from PostgreSQL.")
    st.info("The database connection works, but a dashboard operation failed.")

    with st.expander("Technical details", expanded=True):
        st.code(traceback.format_exc())

    st.stop()


# --------------------------------------------------
# METRICS
# --------------------------------------------------

summary = data["summary"].iloc[0]
valid_events = int(summary["total_events"])
rejected_events = int(data["rejection_summary"].iloc[0]["rejected_events"])
total_processed = valid_events + rejected_events

rejection_rate = (
    rejected_events / total_processed * 100
    if total_processed
    else 0
)

if page == "Executive Overview":
    section_heading(
        "Executive Overview",
        "A high-level view of event ingestion and platform health.",
    )

    kpi_columns = st.columns(4)

    with kpi_columns[0]:
        metric_card("TOTAL PROCESSED", f"{total_processed:,}", "Valid + rejected events")

    with kpi_columns[1]:
        metric_card("VALID EVENTS", f"{valid_events:,}", "Stored successfully")

    with kpi_columns[2]:
        metric_card("REJECTED EVENTS", f"{rejected_events:,}", "Failed validation")

    with kpi_columns[3]:
        metric_card("REJECTION RATE", f"{rejection_rate:.2f}%", "Of all processed events")

    st.write("")

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        section_heading(
            "Event Distribution",
            "Breakdown of accepted events by business event type.",
        )

        event_types = data["event_types"]

        if not event_types.empty:
            fig = px.bar(
                event_types,
                x="event_type",
                y="total",
                text="total",
                color="event_type",
                color_discrete_sequence=[
                    "#5269E8",
                    "#16A085",
                    "#F0A44B",
                    "#8B70D6",
                    "#E77979",
                ],
            )
            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
            )
            fig.update_layout(
                xaxis_title="Event type",
                yaxis_title="Number of events",
            )
            fig = style_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid events are available yet.")

    with chart_right:
        section_heading(
            "Validation Failures",
            "Most common reasons for rejecting incoming events.",
        )

        reasons = data["rejection_reasons"]

        if not reasons.empty:
            fig = px.bar(
                reasons.sort_values("total"),
                x="total",
                y="reason",
                orientation="h",
                text="total",
                color_discrete_sequence=["#E88A52"],
            )
            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
            )
            fig.update_layout(
                xaxis_title="Number of failures",
                yaxis_title="",
            )
            fig = style_chart(fig, horizontal=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No validation failures recorded.")

    section_heading(
        "Activity in the Last 24 Hours",
        "Hourly volume of accepted events.",
    )

    hourly = data["hourly"]

    if not hourly.empty:
        fig = px.area(
            hourly,
            x="hour",
            y="total",
            markers=True,
            color_discrete_sequence=["#5269E8"],
        )
        fig.update_traces(
            fill="tozeroy",
            line=dict(width=3),
        )
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Accepted events",
        )
        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No accepted events in the last 24 hours.")

    section_heading(
        "Recent Events",
        "The 10 latest accepted business events.",
    )
    st.dataframe(
        data["recent_events"].head(10),
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# EVENT MONITORING PAGE
# --------------------------------------------------

elif page == "Event Monitoring":
    section_heading(
        "Event Monitoring",
        "Inspect recently accepted events stored in PostgreSQL.",
    )

    events = data["recent_events"]

    filter_col, search_col = st.columns([1, 2])

    with filter_col:
        available_types = ["All"] + sorted(
            events["event_type"].dropna().unique().tolist()
        )
        selected_type = st.selectbox(
            "Filter by event type",
            available_types,
        )

    with search_col:
        search_term = st.text_input(
            "Search event or user ID",
            placeholder="Enter an event ID or user ID...",
        )

    filtered = events.copy()

    if selected_type != "All":
        filtered = filtered[
            filtered["event_type"] == selected_type
        ]

    if search_term.strip():
        mask = (
            filtered["event_id"].astype(str).str.contains(
                search_term, case=False, na=False
            )
            | filtered["user_id"].astype(str).str.contains(
                search_term, case=False, na=False
            )
        )
        filtered = filtered[mask]

    st.caption(f"Showing {len(filtered)} matching events.")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

    if not filtered.empty:
        st.download_button(
            "Download filtered events as CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="business_events.csv",
            mime="text/csv",
        )


# --------------------------------------------------
# DATA QUALITY PAGE
# --------------------------------------------------

elif page == "Data Quality":
    section_heading(
        "Data Quality Center",
        "Monitor rejected records and understand validation failures.",
    )

    quality_cols = st.columns(3)

    with quality_cols[0]:
        metric_card(
            "PROCESSED EVENTS",
            f"{total_processed:,}",
            "All recorded events",
        )

    with quality_cols[1]:
        metric_card(
            "REJECTED EVENTS",
            f"{rejected_events:,}",
            "Events that failed validation",
        )

    with quality_cols[2]:
        metric_card(
            "REJECTION RATE",
            f"{rejection_rate:.2f}%",
            "Rejected / processed × 100",
        )

    reasons = data["rejection_reasons"]

    section_heading(
        "Rejection Reasons",
        "Counts represent validation-reason occurrences, not necessarily unique events.",
    )

    if not reasons.empty:
        fig = px.bar(
            reasons.sort_values("total"),
            x="total",
            y="reason",
            orientation="h",
            text="total",
            color_discrete_sequence=["#E88A52"],
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Reason occurrences",
            yaxis_title="",
        )
        fig = style_chart(fig, horizontal=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("There are currently no rejected events.")

    section_heading(
        "Rejected Event Records",
        "Review the payload and validation reasons for recent rejected events.",
    )

    rejected_records = data["recent_rejections"]

    if not rejected_records.empty:
        st.dataframe(
            rejected_records,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("No rejected records found.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "Decision Intelligence Platform · Live PostgreSQL metrics · "
    "Built with Streamlit and Plotly"
)
