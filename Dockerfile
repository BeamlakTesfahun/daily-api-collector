FROM python:3.11-slim

WORKDIR /usr/src/app

COPY app/requirements.txt app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY . .
CMD ["python", "app/collector.py"]
