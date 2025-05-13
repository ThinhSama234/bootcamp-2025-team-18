FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
ENV KAFKA_BOOTSTRAP_SERVERS=
ENV KAFKA_LOCATION_TOPIC="location-data"
ENV TRAVELDB_URL=

EXPOSE 8000

CMD ["python", "src/main.py"]