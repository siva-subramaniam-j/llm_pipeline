FROM  python:3.10-slim

RUN export HAYSTACK_TELEMETRY_ENABLED=False

COPY ./* /usr/src/myapp

RUN ["pip", "install", "-r", "/usr/src/myapp/requirements.txt"]
EXPOSE 8000
RUN export PG_CONN_STR=postgresql://postgres:postgres@host.docker.internal:5432/postgres

RUN echo $PG_CONN_STR

ENTRYPOINT ["python", "/usr/src/myapp/main.py"]