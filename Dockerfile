FROM apache/airflow:2.8.1-python3.10

ENV AIRFLOW_HOME=/opt/airflow
WORKDIR /opt/airflow

ENV PYTHONBUFFERED=0
ENV AIRFLOW__LOGGING__LOGGING_LEVEL=INFO

# install your pip packages
COPY requirements.txt ./requirements.txt

COPY dags ./dags
COPY airflow.cfg ./airflow.cfg

RUN pip install --upgrade pip &&\
    pip install --no-cache-dir --upgrade setuptools==59.1.1 &&\
    pip install --no-cache-dir --upgrade wheel &&\
    pip install --no-cache-dir --user -r requirements.txt
