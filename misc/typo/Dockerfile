FROM python:slim as app

RUN pip install --no-cache-dir pycryptodome


FROM pwn.red/jail
COPY --from=app / /srv

COPY ./src/server.py /srv/app/run
COPY ./flag.txt /srv/app/flag.txt

ENV JAIL_MEM=20M JAIL_TMP_SIZE=1M JAIL_PIDS=100 JAIL_CPU=0 JAIL_TIME=10
ENV JAIL_ENV_PYTHONUNBUFFERED=1 JAIL_ENV_PATH=/usr/local/bin:/usr/bin:/bin
