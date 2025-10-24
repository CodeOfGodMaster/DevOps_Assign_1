FROM python:3.9-slim
WORKDIR /app
COPY s3_to_rds_glue.py .
RUN pip install boto3 psycopg2-binary
CMD ["python", "s3_to_rds_glue.py"]
