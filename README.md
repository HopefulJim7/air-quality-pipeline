# Real-Time Air Quality Monitoring Pipeline

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Open%20App-brightgreen?style=for-the-badge)](https://air-quality-pipeline-qe4cee8rgmqbvrwzc3hmhh.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)](https://kafka.apache.org)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

![Dashboard Preview](assets/01_aqi_cards.png)

A production-grade, end-to-end real-time data engineering pipeline that
collects, processes, stores, and visualizes air quality data from 5 major
cities across the globe — updated every 10 minutes using live data from
the OpenWeather API.

---

## Who This Helps

### Public Health Organizations & Ministries of Health
Real-time pollution monitoring enables early warning systems for vulnerable
populations — children, the elderly, and those with respiratory conditions.
Agencies can integrate this pipeline to trigger public health advisories
automatically when AQI thresholds are exceeded.

### Environmental Protection Agencies
Continuous, automated data collection replaces manual monitoring with a
scalable system that tracks PM2.5, PM10, NO2, O3, SO2, and CO across
multiple cities simultaneously — providing the evidence base for
environmental policy decisions.

### Urban Planning & Smart City Initiatives
City planners can use historical trend data to correlate pollution spikes
with traffic patterns, industrial activity, or weather events — informing
decisions on zoning, green spaces, and transportation infrastructure.

### Research Institutions & Universities
The structured data warehouse (star schema) makes this pipeline ready for
academic research — longitudinal studies on pollution trends, cross-city
comparisons, and climate impact analysis.

### NGOs & Advocacy Groups
Transparent, publicly accessible air quality data empowers community
advocacy. Organizations working on environmental justice can use this
dashboard to document pollution disparities across cities and regions.

---

## Dashboard Screenshots

![AQI Cards](assets/01_aqi_cards.png)
*Real-time AQI cards with color-coded health categories for each city*

![PM2.5 Trend](assets/02_pm25_trend.png)
*PM2.5 concentration trends over time with alert threshold line*

![City Comparison](assets/03_city_comparison.png)
*Side-by-side city comparison — PM2.5 and AQI bar charts*

![Active Alerts](assets/05_alerts.png)
*Real-time alert monitoring — CRITICAL and WARNING threshold violations*

![Raw Data](assets/06_raw_data.png)
*Complete raw data table with all pollutant readings*

---

## Architecture