import os
os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["PATH"] = "C:\\hadoop\\bin;" + os.environ.get("PATH", "")

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, to_timestamp
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, DoubleType
)
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5433")
DB_NAME     = os.getenv("DB_NAME", "airqualitydb")
DB_USER     = os.getenv("DB_USER", "airquality")
DB_PASSWORD = os.getenv("DB_PASSWORD", "airquality123")
JDBC_URL    = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

DB_PROPERTIES = {
    "user":     DB_USER,
    "password": DB_PASSWORD,
    "driver":   "org.postgresql.Driver"
}

THRESHOLDS = {
    "pm25": 35.0,
    "pm10": 50.0,
    "no2":  100.0,
    "aqi":  4,
}

SCHEMA = StructType([
    StructField("city_id",   IntegerType(), True),
    StructField("city_name", StringType(),  True),
    StructField("timestamp", StringType(),  True),
    StructField("aqi",       IntegerType(), True),
    StructField("pm25",      DoubleType(),  True),
    StructField("pm10",      DoubleType(),  True),
    StructField("co",        DoubleType(),  True),
    StructField("no2",       DoubleType(),  True),
    StructField("o3",        DoubleType(),  True),
    StructField("so2",       DoubleType(),  True),
])


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("AirQualityStreamProcessor")
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                "org.postgresql:postgresql:42.6.0")
        .config("spark.sql.streaming.checkpointLocation", "./checkpoints")
        .config("spark.driver.memory", "512m")
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
        .config("spark.hadoop.fs.AbstractFileSystem.file.impl", "org.apache.hadoop.fs.local.LocalFs")
        .getOrCreate()
    )


def write_to_postgres(df, table: str):
    df.write.jdbc(url=JDBC_URL, table=table, mode="append", properties=DB_PROPERTIES)


def process_batch(batch_df, batch_id: int):
    if batch_df.isEmpty():
        return

    print(f"\n── Batch {batch_id} ── {batch_df.count()} records ──")

    # 1. Write all records to fact_air_quality
    air_quality_df = batch_df.select(
        "city_id",
        to_timestamp(col("timestamp")).alias("timestamp"),
        "pm25", "pm10", "co", "no2", "o3", "so2", "aqi"
    )
    write_to_postgres(air_quality_df, "fact_air_quality")
    print(f"  ✓ Wrote {air_quality_df.count()} records to fact_air_quality")

    # 2. Check thresholds and generate alerts
    alerts = []

    checks = [
        ("pm25", THRESHOLDS["pm25"]),
        ("pm10", THRESHOLDS["pm10"]),
        ("no2",  THRESHOLDS["no2"]),
    ]

    for pollutant, threshold in checks:
        violated = batch_df.filter(col(pollutant) > threshold) \
         .withColumn("pollutant",      when(col("city_id") >= 0, pollutant)) \
         .withColumn("threshold",      when(col("city_id") >= 0, threshold)) \
         .withColumn("measured_value", col(pollutant)) \
         .withColumn("alert_level",    when(col(pollutant) > threshold * 2, "CRITICAL")
                                       .otherwise("WARNING")) \
         .select(
             "city_id",
             to_timestamp(col("timestamp")).alias("timestamp"),
             "pollutant", "threshold", "measured_value", "alert_level"
         )
        alerts.append(violated)

    # AQI alert check
    aqi_violated = batch_df.filter(col("aqi") > THRESHOLDS["aqi"]) \
     .withColumn("pollutant",      when(col("city_id") >= 0, "aqi")) \
     .withColumn("threshold",      when(col("city_id") >= 0, float(THRESHOLDS["aqi"]))) \
     .withColumn("measured_value", col("aqi").cast(DoubleType())) \
     .withColumn("alert_level",    when(col("aqi") == 5, "CRITICAL")
                                   .otherwise("WARNING")) \
     .select(
         "city_id",
         to_timestamp(col("timestamp")).alias("timestamp"),
         "pollutant", "threshold", "measured_value", "alert_level"
     )
    alerts.append(aqi_violated)

    from functools import reduce
    from pyspark.sql import DataFrame

    all_alerts = reduce(DataFrame.unionAll, alerts)

    if not all_alerts.isEmpty():
        write_to_postgres(all_alerts, "fact_alerts")
        print(f"  ⚠ Wrote {all_alerts.count()} alerts to fact_alerts")
    else:
        print(f"  ✓ No threshold violations in this batch")


def run():
    print("Starting Spark Structured Streaming Processor...")

    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    raw_stream = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "air_quality_data")
        .option("startingOffsets", "latest")
        .load()
    )

    parsed_stream = (
        raw_stream
        .selectExpr("CAST(value AS STRING) as json_str")
        .select(from_json(col("json_str"), SCHEMA).alias("data"))
        .select("data.*")
    )

    query = (
        parsed_stream.writeStream
        .foreachBatch(process_batch)
        .option("checkpointLocation", "./checkpoints")
        .trigger(processingTime="30 seconds")
        .start()
    )

    print("Streaming query started. Waiting for data from Kafka...")
    print("(Press Ctrl+C to stop)\n")
    query.awaitTermination()


if __name__ == "__main__":
    run()