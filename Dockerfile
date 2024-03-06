FROM apache/airflow:2.8.2-python3.8

ENV PYTHONBUFFERED=0
ENV AIRFLOW__LOGGING__LOGGING_LEVEL=INFO

# install your pip packages
COPY requirements.txt ./requirements.txt
COPY requirements-test.txt ./requirements-test.txt

COPY dags ./dags

RUN pip install --no-cache-dir --user  -r requirements-test.txt -r requirements.txt
