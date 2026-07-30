FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker ./worker

USER 10001

EXPOSE 9000

CMD ["python", "-m", "worker.main"]
