# app/main.py
import csv
import io
import sys
import logging
import time
from typing import Iterable

import boto3
import psycopg2
from botocore.exceptions import ClientError, NoCredentialsError

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger()

# Config values (update as needed)
INPUT_MODE = "local"  # Change to "s3" when using AWS S3
S3_BUCKET = "akshay-devops-pipe-10252025"
S3_KEY = "sample-data.csv"
PG_CONN = "postgresql://postgres:password@your-rds-endpoint:5432/yourdbname"
GLUE_DATABASE = "fallback_database"
GLUE_TABLE = "fallback_table"
REGION = "us-east-1"


# Read CSV file from S3
def read_csv_from_s3(bucket: str, key: str) -> Iterable[list]:
    s3 = boto3.client("s3", region_name=REGION)
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    return csv.reader(io.StringIO(content))


# Read CSV file locally
def read_csv_local(path="app/sample/data.csv"):
    with open(path, newline="") as f:
        return csv.reader(f)


# Insert data into PostgreSQL
def write_to_postgres(rows: Iterable[list]):
    conn = psycopg2.connect(PG_CONN)
    cur = conn.cursor()

    insert_sql = "INSERT INTO mytable(col1, col2) VALUES (%s, %s)"
    count = 0

    for r in rows:
        if r and r[0].lower().startswith("col"):  # skip header
            continue
        cur.execute(insert_sql, (r[0], r[1] if len(r) > 1 else None))
        count += 1

    conn.commit()
    cur.close()
    conn.close()
    LOG.info("Inserted %d rows into PostgreSQL", count)


# Store data in S3 as fallback
def push_to_s3_for_glue(bucket: str, key_prefix: str, rows: Iterable[list]):
    s3_key = f"{key_prefix}/fallback_{int(time.time())}.csv"
    buf = io.StringIO()
    writer = csv.writer(buf)

    for r in rows:
        writer.writerow(r)

    s3 = boto3.client("s3", region_name=REGION)
    s3.put_object(Bucket=bucket, Key=s3_key, Body=buf.getvalue().encode("utf-8"))
    LOG.info("Fallback file uploaded → s3://%s/%s", bucket, s3_key)
    return s3_key


# Add fallback data to Glue Catalog
def create_glue_db_and_table(bucket: str, key: str, db_name: str, table_name: str):
    glue = boto3.client("glue", region_name=REGION)

    try:
        glue.create_database(DatabaseInput={"Name": db_name})
    except glue.exceptions.AlreadyExistsException:
        pass

    table_input = {
        "Name": table_name,
        "StorageDescriptor": {
            "Columns": [
                {"Name": "col1", "Type": "string"},
                {"Name": "col2", "Type": "string"},
            ],
            "Location": f"s3://{bucket}/{key}",
        },
        "TableType": "EXTERNAL_TABLE",
    }

    try:
        glue.create_table(DatabaseName=db_name, TableInput=table_input)
    except glue.exceptions.AlreadyExistsException:
        pass


# Main flow
def main():
    try:
        rows = list(read_csv_from_s3(S3_BUCKET, S3_KEY)) if INPUT_MODE == "s3" else list(read_csv_local())

        try:
            write_to_postgres(rows)
        except Exception as e:
            LOG.error("Data insert failed: %s", e)
            fallback_key = push_to_s3_for_glue(S3_BUCKET, "fallback", rows)
            create_glue_db_and_table(S3_BUCKET, fallback_key, GLUE_DATABASE, GLUE_TABLE)

    except NoCredentialsError:
        LOG.error("Missing AWS credentials")
        sys.exit(2)
    except ClientError as e:
        LOG.error("AWS error: %s", e)
        sys.exit(3)


if __name__ == "__main__":
    main()
