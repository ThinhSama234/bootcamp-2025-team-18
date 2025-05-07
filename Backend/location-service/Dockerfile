FROM python:3.10.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

ENV FLASK_PORT=5000
ENV GRPC_PORT=50051

CMD ["python", "src/main.py"]
