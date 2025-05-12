FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
ENV INGEST_SERVICE_URL=
ENV BATCH_SIZE=

EXPOSE 8000

CMD ["python", "src/main.py"]