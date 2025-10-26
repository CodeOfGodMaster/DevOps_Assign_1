FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install boto3 psycopg2-binary
COPY . /app
CMD ["python", "imp.py"]
