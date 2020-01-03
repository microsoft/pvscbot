FROM python:3.8

COPY requirements.txt .
RUN pip --disable-pip-version-check --no-cache-dir install -r requirements.txt

COPY pvscbot ./pvscbot/
#ENTRYPOINT ["python", "-m", "pvscbot"]
ENTRYPOINT ["ls"]
