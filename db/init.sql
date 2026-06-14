-- City dimension table
CREATE TABLE IF NOT EXISTS dim_city (
    city_id     SERIAL PRIMARY KEY,
    city_name   VARCHAR(100) NOT NULL,
    country     VARCHAR(10),
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6)
);

-- Air quality facts table
CREATE TABLE IF NOT EXISTS fact_air_quality (
    record_id   SERIAL PRIMARY KEY,
    city_id     INT REFERENCES dim_city(city_id),
    timestamp   TIMESTAMP NOT NULL,
    pm25        NUMERIC(8,2),
    pm10        NUMERIC(8,2),
    co          NUMERIC(8,2),
    no2         NUMERIC(8,2),
    o3          NUMERIC(8,2),
    so2         NUMERIC(8,2),
    aqi         INT
);

-- Alerts table
CREATE TABLE IF NOT EXISTS fact_alerts (
    alert_id        SERIAL PRIMARY KEY,
    city_id         INT REFERENCES dim_city(city_id),
    timestamp       TIMESTAMP NOT NULL,
    pollutant       VARCHAR(20),
    threshold       NUMERIC(8,2),
    measured_value  NUMERIC(8,2),
    alert_level     VARCHAR(20)
);

-- Seed some cities
INSERT INTO dim_city (city_name, country, latitude, longitude) VALUES
    ('Nairobi',   'KE', -1.286389,  36.817223),
    ('London',    'GB', 51.507351,  -0.127758),
    ('New York',  'US', 40.712776, -74.005974),
    ('Delhi',     'IN', 28.613939,  77.209023),
    ('Beijing',   'CN', 39.904202, 116.407394)
ON CONFLICT DO NOTHING;