FROM python:slim AS python-crypto
RUN pip install --no-cache-dir pycryptodome

FROM pwn.red/jail
COPY --from=python-crypto / /srv
COPY ./dist/chall.py /srv/app/run
RUN chmod +x /srv/app/run
COPY ./key /srv/app/key
COPY ./flag.txt /srv/app/flag.txt

ENV JAIL_MEM=20M JAIL_POW=6000 JAIL_TIME=30
