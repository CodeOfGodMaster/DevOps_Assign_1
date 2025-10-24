import boto3
import psycopg2

def read_from_s3(bucket, key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8')
    return data

def push_to_rds(data, rds_config):
    try:
        conn = psycopg2.connect(**rds_config)
        cur = conn.cursor()
        # insert data into RDS table
        cur.execute("INSERT INTO your_table (column) VALUES (%s)", (data,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f'RDS error: {e}')
        return False

def push_to_glue(data, glue_config):
    glue = boto3.client('glue')
    # Example Glue usage, customize as needed
    # Glue ETL jobs or Glue catalog table update goes here
    print('Pushing data to Glue')
    return True

def main():
    bucket = 'your-bucket'
    key = 'your-file-key'
    rds_config = {'host': 'rds-host', 'database': 'db-name', 'user': 'user', 'password': 'pass'}

    data = read_from_s3(bucket, key)
    if not push_to_rds(data, rds_config):
        push_to_glue(data, {})

if __name__ == "__main__":
    main()
