# app/main.py
import os
import csv
import io
import sys
import logging
from typing import Iterable

import boto3
import psycopg2
from botocore.exceptions import ClientError, NoCredentialsError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger(__name__)

# Config (env vars)
INPUT_MODE = os.getenv("INPUT_MODE", "local")   # "s3" or "local"
S3_BUCKET = os.getenv("S3_BUCKET", "my-data-bucket")
S3_KEY = os.getenv("S3_KEY", "data.csv")
PG_CONN = os.getenv("PG_CONN", "postgresql://user:pass@host:5432/dbname")
GLUE_DATABASE = os.getenv("GLUE_DATABASE", "dev_fallback_db")
GLUE_TABLE = os.getenv("GLUE_TABLE", "fallback_table")
REGION = os.getenv("AWS_REGION", "us-east-1")

def read_csv_from_s3(bucket: str, key: str) -> Iterable[list]:
    LOG.info("Reading from S3 s3://%s/%s", bucket, key)
    s3 = boto3.client("s3", region_name=REGION)
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read().decode('utf-8')
    reader = csv.reader(io.StringIO(body))
    for row in reader:
        yield row

def read_csv_local(path="app/sample/data.csv"):
    LOG.info("Reading local file %s", path)
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            yield row

def write_to_postgres(rows: Iterable[list]):
    LOG.info("Attempting to write to Postgres")
    conn = psycopg2.connect(PG_CONN)
    cur = conn.cursor()
    # Example table: mytable(col1 text, col2 text)
    insert_sql = "INSERT INTO mytable(col1, col2) VALUES (%s, %s)"
    count = 0
    for r in rows:
        # skip header when detected
        if r and r[0].lower().startswith("col"):
            continue
        cur.execute(insert_sql, (r[0], r[1] if len(r) > 1 else None))
        count += 1
    conn.commit()
    cur.close()
    conn.close()
    LOG.info("Inserted %d rows into Postgres", count)
    return count

def push_to_s3_for_glue(bucket: str, key_prefix: str, rows: Iterable[list]) -> str:
    s3 = boto3.client("s3", region_name=REGION)
    out_key = f"{key_prefix}/fallback_{int(__import__('time').time())}.csv"
    buf = io.StringIO()
    writer = csv.writer(buf)
    wrote = 0
    for r in rows:
        writer.writerow(r)
        wrote += 1
    s3.put_object(Bucket=bucket, Key=out_key, Body=buf.getvalue().encode('utf-8'))
    LOG.info("Uploaded fallback CSV to s3://%s/%s (%d rows)", bucket, out_key, wrote)
    return out_key

def create_glue_db_and_table(bucket: str, key: str, db_name: str, table_name: str):
    glue = boto3.client("glue", region_name=REGION)
    try:
        glue.create_database(DatabaseInput={'Name': db_name})
        LOG.info("Glue database %s created or already exists", db_name)
    except glue.exceptions.AlreadyExistsException:
        LOG.info("Glue DB already exists")

    table_input = {
        'Name': table_name,
        'StorageDescriptor': {
            'Columns': [{'Name': 'col1', 'Type': 'string'}, {'Name': 'col2', 'Type': 'string'}],
            'Location': f"s3://{bucket}/{key}",
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {'SerializationLibrary': 'org.apache.hadoop.hive.serde2.OpenCSVSerde',
                         'Parameters': {'separatorChar': ',', 'quoteChar': '"'}}
        },
        'TableType': 'EXTERNAL_TABLE'
    }
    try:
        glue.create_table(DatabaseName=db_name, TableInput=table_input)
        LOG.info("Glue table %s.%s created", db_name, table_name)
    except glue.exceptions.AlreadyExistsException:
        LOG.info("Glue table already exists")

def main():
    try:
        if INPUT_MODE == "s3":
            rows = list(read_csv_from_s3(S3_BUCKET, S3_KEY))
        else:
            rows = list(read_csv_local())
        try:
            write_to_postgres(rows)
            LOG.info("Successfully wrote to Postgres")
        except Exception as e:
            LOG.exception("Writing to Postgres failed: %s", e)
            # fallback: push CSV to S3 and register in Glue
            out_key = push_to_s3_for_glue(S3_BUCKET, "fallback", rows)
            create_glue_db_and_table(S3_BUCKET, out_key, GLUE_DATABASE, GLUE_TABLE)
    except NoCredentialsError:
        LOG.exception("AWS credentials not found")
        sys.exit(2)
    except ClientError as e:
        LOG.exception("AWS client error: %s", e)
        sys.exit(3)

if __name__ == "__main__":
    main()
