FROM apache/airflow:2.10.5-python3.11

COPY docker/airflow/requirements.txt /tmp/airflow-project-requirements.txt

RUN pip install --no-cache-dir \
    --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt \
    -r /tmp/airflow-project-requirements.txt
