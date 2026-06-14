import json
import time
import requests
import os
from datetime import datetime, timezone
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
KAFKA_BROKER = "localhost:9092"
TOPIC = "air_quality_data"

# Cities to monitor — must match what's in dim_city
CITIES = [
    {"city_id": 1, "name": "Nairobi",  "lat": -1.286389, "lon":  36.817223},
    {"city_id": 2, "name": "London",   "lat": 51.507351, "lon":  -0.127758},
    {"city_id": 3, "name": "New York", "lat": 40.712776, "lon": -74.005974},
    {"city_id": 4, "name": "Delhi",    "lat": 28.613939, "lon":  77.209023},
    {"city_id": 5, "name": "Beijing",  "lat": 39.904202, "lon": 116.407394},
]


def fetch_air_quality(city: dict) -> dict | None:
    """Call the OpenWeather Air Pollution API for one city."""
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={city['lat']}&lon={city['lon']}&appid={API_KEY}"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        entry = data["list"][0]
        components = entry["components"]

        return {
            "city_id":   city["city_id"],
            "city_name": city["name"],
            "timestamp": datetime.fromtimestamp(entry["dt"], timezone.utc).isoformat(),
            "aqi":       entry["main"]["aqi"],
            "pm25":      components.get("pm2_5"),
            "pm10":      components.get("pm10"),
            "co":        components.get("co"),
            "no2":       components.get("no2"),
            "o3":        components.get("o3"),
            "so2":       components.get("so2"),
        }

    except Exception as e:
        print(f"  [ERROR] Failed to fetch data for {city['name']}: {e}")
        return None


def create_producer() -> KafkaProducer:
    """Create and return a Kafka producer."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )


def run():
    """Main loop — fetch and publish every 60 seconds."""
    print("Starting Air Quality Producer...")
    print(f"Publishing to Kafka topic: '{TOPIC}'")
    print("-" * 40)

    producer = create_producer()

    while True:
        print(f"\n[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Fetching data for all cities...")

        for city in CITIES:
            record = fetch_air_quality(city)

            if record:
                producer.send(TOPIC, value=record)
                print(f"  ✓ {city['name']:10s} | AQI: {record['aqi']} | "
                      f"PM2.5: {record['pm25']} | PM10: {record['pm10']}")
            
        producer.flush()
        print(f"  All records published. Waiting 10 minutes...")
        time.sleep(600) #(600) to (60) for every- 1 minute(60seconds). (600) for every 10 minutes - To reduce api usage.


if __name__ == "__main__":
    run()