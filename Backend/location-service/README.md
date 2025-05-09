
# How to run & build

- Run `pip install -r requirements.txt`.
- Run `python3 -m grpc_tools.protoc -I./src/proto --python_out=./src/generated --grpc_python_out=./src/generated src/proto/location_service.proto` to generate gRPC classes. After that, go to `src/generated/location_service_pb2_grpc.py` and change the line:
  `import location_service_pb2 as location__service__pb2`
to `from . import location_service_pb2 as location__service__pb2`.
- Create a .env file and fill in the variables like in `.env.sample`.
- Run `python src/main.py` to start the service.