import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Air Quality Monitor",
    page_icon="🌍",
    layout="wide"
)

# ── Database connection ────────────────────────────────────────────────────────
def get_engine():
    return create_engine(
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER', 'airquality')}:"
        f"{os.getenv('DB_PASSWORD', 'airquality123')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5433')}/"
        f"{os.getenv('DB_NAME', 'airqualitydb')}"
    )

def run_query(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)

# ── AQI helper ─────────────────────────────────────────────────────────────────
AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
AQI_COLORS = {1: "#00e400", 2: "#ffff00", 3: "#ff7e00", 4: "#ff0000", 5: "#8f3f97"}

def aqi_label(val):
    return AQI_LABELS.get(int(val), "Unknown")

def aqi_color(val):
    return AQI_COLORS.get(int(val), "#gray")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🌍 Real-Time Air Quality Monitor")
st.caption("Data refreshes every 30 seconds · Powered by OpenWeather API")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Live AQI per City
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📊 Current AQI by City")

latest_sql = """
    SELECT DISTINCT ON (f.city_id)
        c.city_name,
        f.aqi,
        f.pm25,
        f.pm10,
        f.no2,
        f.timestamp
    FROM fact_air_quality f
    JOIN dim_city c ON f.city_id = c.city_id
    ORDER BY f.city_id, f.timestamp DESC
"""
latest_df = run_query(latest_sql)

if not latest_df.empty:
    cols = st.columns(len(latest_df))
    for i, row in latest_df.iterrows():
        with cols[i]:
            color = aqi_color(row["aqi"])
            label = aqi_label(row["aqi"])
            st.markdown(
                f"""
                <div style="
                    background-color:{color}22;
                    border-left: 5px solid {color};
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;">
                    <h4 style="margin:0">{row['city_name']}</h4>
                    <h2 style="margin:4px 0;color:{color}">AQI {row['aqi']}</h2>
                    <p style="margin:0;font-size:0.85em">{label}</p>
                    <hr style="margin:6px 0">
                    <small>PM2.5: {row['pm25']} · PM10: {row['pm10']}</small><br>
                    <small>NO₂: {row['no2']}</small><br>
                    <small style="color:gray">{pd.to_datetime(row['timestamp']).strftime('%H:%M:%S')}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — PM2.5 Trend Over Time
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📈 PM2.5 Trend Over Time")

trend_sql = """
    SELECT c.city_name, f.timestamp, f.pm25
    FROM fact_air_quality f
    JOIN dim_city c ON f.city_id = c.city_id
    ORDER BY f.timestamp
"""
trend_df = run_query(trend_sql)

if not trend_df.empty:
    fig = px.line(
        trend_df,
        x="timestamp", y="pm25",
        color="city_name",
        title="PM2.5 Levels Over Time",
        labels={"pm25": "PM2.5 (μg/m³)", "timestamp": "Time", "city_name": "City"},
        template="plotly_dark"
    )
    fig.add_hline(
        y=35, line_dash="dash", line_color="red",
        annotation_text="Alert Threshold (35)"
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — City Comparison Bar Chart
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🏙️ City Comparison — Latest Readings")

if not latest_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig_pm25 = px.bar(
            latest_df.sort_values("pm25", ascending=False),
            x="city_name", y="pm25",
            color="pm25",
            color_continuous_scale="RdYlGn_r",
            title="PM2.5 by City",
            labels={"pm25": "PM2.5 (μg/m³)", "city_name": "City"},
            template="plotly_dark"
        )
        fig_pm25.add_hline(y=35, line_dash="dash", line_color="red")
        st.plotly_chart(fig_pm25, use_container_width=True)

    with col2:
        fig_aqi = px.bar(
            latest_df.sort_values("aqi", ascending=False),
            x="city_name", y="aqi",
            color="aqi",
            color_continuous_scale="RdYlGn_r",
            title="AQI by City",
            labels={"aqi": "AQI", "city_name": "City"},
            template="plotly_dark"
        )
        fig_aqi.add_hline(y=4, line_dash="dash", line_color="red")
        st.plotly_chart(fig_aqi, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Active Alerts
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🚨 Active Alerts")

alerts_sql = """
    SELECT
        c.city_name,
        a.pollutant,
        a.measured_value,
        a.threshold,
        a.alert_level,
        a.timestamp
    FROM fact_alerts a
    JOIN dim_city c ON a.city_id = c.city_id
    ORDER BY a.timestamp DESC
    LIMIT 20
"""
alerts_df = run_query(alerts_sql)

if alerts_df.empty:
    st.success("✅ No active alerts — all cities within safe limits")
else:
    def style_alert(val):
        if val == "CRITICAL":
            return "background-color: #ff000033; color: red; font-weight: bold"
        elif val == "WARNING":
            return "background-color: #ff7e0033; color: orange"
        return ""

    st.dataframe(
        alerts_df.style.map(style_alert, subset=["alert_level"]),
        use_container_width=True
    )
    st.caption(f"Showing last 20 alerts · Total records: {len(alerts_df)}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Raw Data Table
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("🔍 View Raw Data"):
    raw_sql = """
        SELECT c.city_name, f.timestamp, f.aqi, f.pm25, f.pm10, f.co, f.no2, f.o3, f.so2
        FROM fact_air_quality f
        JOIN dim_city c ON f.city_id = c.city_id
        ORDER BY f.timestamp DESC
        LIMIT 50
    """
    raw_df = run_query(raw_sql)
    st.dataframe(raw_df, use_container_width=True)
    
# ── Silent background refresh ─────────────────────────────────────────────────
st.sidebar.markdown("### ⚙️ Settings")
refresh_rate = st.sidebar.selectbox(
    "Refresh interval",
    options=[30, 60, 120, 300],
    format_func=lambda x: f"Every {x} seconds"
)

placeholder = st.sidebar.empty()
for remaining in range(refresh_rate, 0, -1):
    placeholder.caption(f"🔄 Refreshing in {remaining}s...")
    time.sleep(1)

st.rerun()