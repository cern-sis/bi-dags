FROM registry.cern.ch/cern-sis/airflow-base:2.8.3

ENV PYTHONBUFFERED=0
ENV AIRFLOW__LOGGING__LOGGING_LEVEL=INFO

# install your pip packages
COPY requirements.txt ./requirements.txt
COPY requirements-test.txt ./requirements-test.txt

COPY dags ./dags

RUN pip install -r requirements-test.txt -r requirements.txt
