FROM python:3.10.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ ./src

ENV GRPC_PORT=50051
ENV TRAVELDB_URL=

EXPOSE 50051

CMD ["python", "src/main.py"]
