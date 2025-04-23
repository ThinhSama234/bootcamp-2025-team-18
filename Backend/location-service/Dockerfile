FROM python:3.12.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 -m grpc_tools.protoc -I./src/proto --python_out=./src/generated --grpc_python_out=./src/generated src/proto/location_service.proto

ENV FLASK_PORT=5000
ENV GRPC_PORT=50051

CMD ["python", "src/main.py"]
