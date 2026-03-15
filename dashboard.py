import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from config import DB_PATH, REPORT_PDF_PATH
from db_setup import load_csv_to_sqlite
from run_analysis import run_all_queries, get_summary_metrics

st.set_page_config(
    page_title="Ola Rides Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(165deg, #f0f9ff 0%, #e0f2fe 35%, #fefce8 100%); }
    .main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }
    [data-testid="stMetricValue"] { font-size: 1.9rem !important; font-weight: 700 !important; color: #0f172a !important; }
    [data-testid="stMetricLabel"] { font-size: 0.9rem !important; font-weight: 600 !important; color: #475569 !important; letter-spacing: 0.02em; }
    div[data-testid="metric-container"] {
        background: #ffffff !important;
        padding: 1.25rem 1.5rem !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(0,0,0,0.06) !important;
        border-left: 4px solid #0ea5e9 !important;
    }
    div[data-testid="metric-container"]:nth-of-type(1) { border-left-color: #0ea5e9 !important; }
    div[data-testid="metric-container"]:nth-of-type(2) { border-left-color: #10b981 !important; }
    div[data-testid="metric-container"]:nth-of-type(3) { border-left-color: #f59e0b !important; }
    div[data-testid="metric-container"]:nth-of-type(4) { border-left-color: #8b5cf6 !important; }
    h1 { color: #0f172a !important; font-weight: 800 !important; letter-spacing: -0.02em !important; }
    h2 { color: #1e293b !important; font-weight: 700 !important; margin-top: 2rem !important; padding-bottom: 0.5rem !important; border-bottom: 2px solid #e2e8f0 !important; }
    h3 { color: #334155 !important; font-weight: 600 !important; }
    .streamlit-expanderHeader { background: #f8fafc !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def ensure_db():
    if not Path(DB_PATH).exists():
        load_csv_to_sqlite()
    return DB_PATH

@st.cache_data(ttl=300)
def load_metrics():
    ensure_db()
    return get_summary_metrics()

@st.cache_data(ttl=300)
def load_query_results():
    ensure_db()
    return run_all_queries()

CHART_COLORS = ["#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16", "#f97316"]

def main():
    row0 = st.columns([3, 1])
    with row0[0]:
        st.title("🚗 Ola Rides – Data Analysis Dashboard")
        st.caption("Interactive insights and PDF report download")
    with row0[1]:
        pdf_path = Path(REPORT_PDF_PATH)
        if not pdf_path.exists():
            try:
                from report_generator import build_report
                build_report()
            except Exception:
                pass
        if pdf_path.exists():
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=f.read(),
                    file_name="Ola_Data_Analysis_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            if st.button("📄 Generate & Download Report", use_container_width=True):
                try:
                    from report_generator import build_report
                    build_report()
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    metrics = load_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Bookings", f"{metrics['total_bookings']:,}")
    c2.metric("Successful Rides", f"{metrics['successful_rides']:,}")
    c3.metric("Success Rate", f"{metrics['success_rate_pct']}%")
    c4.metric("Total Revenue (₹)", f"{metrics['total_revenue']:,.0f}")

    results = load_query_results()
    result_map = {r["name"]: r for r in results}

    st.header("Booking status")
    df_status = result_map.get("Q1", {}).get("df")
    if df_status is not None and not df_status.empty:
        fig = px.pie(
            df_status, values="count", names="Booking_Status",
            title="Rides by status", color_discrete_sequence=CHART_COLORS,
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
        st.plotly_chart(fig, use_container_width=True)

    st.header("Vehicle type (successful rides)")
    df_vehicle = result_map.get("Q2", {}).get("df")
    if df_vehicle is not None and not df_vehicle.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.bar(
                df_vehicle, x="Vehicle_Type", y="total_rides",
                title="Rides by vehicle type", color="total_rides",
                color_continuous_scale=["#e0f2fe", "#0ea5e9", "#0369a1"],
            )
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = px.bar(
                df_vehicle, x="Vehicle_Type", y="avg_booking_value",
                title="Avg booking value by vehicle", color="avg_booking_value",
                color_continuous_scale=["#d1fae5", "#10b981", "#047857"],
            )
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
            st.plotly_chart(fig3, use_container_width=True)

    st.header("Payment methods (revenue)")
    df_pay = result_map.get("Q3", {}).get("df")
    if df_pay is not None and not df_pay.empty:
        fig4 = px.pie(
            df_pay, values="total_revenue", names="Payment_Method",
            title="Revenue by payment method", color_discrete_sequence=CHART_COLORS,
        )
        fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
        st.plotly_chart(fig4, use_container_width=True)

    st.header("Top locations")
    df_pickup = result_map.get("Q4", {}).get("df")
    df_drop = result_map.get("Q5", {}).get("df")
    if df_pickup is not None and not df_pickup.empty:
        fig5 = px.bar(df_pickup, x="Pickup_Location", y="ride_count", title="Top 10 pickup locations", color="ride_count", color_continuous_scale=["#ede9fe", "#8b5cf6", "#5b21b6"])
        fig5.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
        st.plotly_chart(fig5, use_container_width=True)
    if df_drop is not None and not df_drop.empty:
        fig6 = px.bar(df_drop, x="Drop_Location", y="ride_count", title="Top 10 drop locations", color="ride_count", color_continuous_scale=["#fce7f3", "#ec4899", "#be185d"])
        fig6.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
        st.plotly_chart(fig6, use_container_width=True)

    st.header("Ratings by vehicle type")
    df_ratings = result_map.get("Q7", {}).get("df")
    if df_ratings is not None and not df_ratings.empty:
        fig7 = go.Figure()
        fig7.add_trace(go.Bar(name="Driver rating", x=df_ratings["Vehicle_Type"], y=df_ratings["avg_driver_rating"], marker_color="#0ea5e9"))
        fig7.add_trace(go.Bar(name="Customer rating", x=df_ratings["Vehicle_Type"], y=df_ratings["avg_customer_rating"], marker_color="#10b981"))
        fig7.update_layout(barmode="group", title="Average driver vs customer rating by vehicle", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
        st.plotly_chart(fig7, use_container_width=True)

    st.header("All query results (tables)")
    for r in results:
        with st.expander(f"{r['name']}: {r['title']}"):
            st.dataframe(r["df"], use_container_width=True)

    st.caption("Use the Download PDF Report button at the top for the full report.")

if __name__ == "__main__":
    main()
