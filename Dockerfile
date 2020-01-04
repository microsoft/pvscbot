FROM python:3.8

COPY requirements.txt /app/
RUN pip --disable-pip-version-check --no-cache-dir install -r /app/requirements.txt

COPY pvscbot /app/pvscbot/

COPY entrypoint.sh /app/
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
