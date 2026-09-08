"""
Online Code Explorer — gRPC workspace monitor

Pure gRPC backend. Query-only: file count, total lines, total bytes.
The HTML frontend does not call this process; use frontend/grpc_client.py.

Start from the project root:
    python3 backend/grpc_service.py

Listens on 127.0.0.1:50051. Aggregation lives in data_logic.py.

Dependencies: grpcio, grpcio-tools, protobuf
"""

import os
import signal
import sys
from concurrent import futures

# Generated stubs live next to this file; keep backend/ on sys.path.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

import grpc

import data_logic
import file_service_pb2
import file_service_pb2_grpc

GRPC_HOST = "127.0.0.1"
GRPC_PORT = 50051
LISTEN_ADDR = "{}:{}".format(GRPC_HOST, GRPC_PORT)


class WorkspaceServiceServicer(file_service_pb2_grpc.WorkspaceServiceServicer):
    """gRPC servicer: protocol mapping only; all disk work is in data_logic."""

    def GetFileCount(self, request, context):
        # TODO
        raise NotImplementedError

    def GetLineCount(self, request, context):
        # TODO
        raise NotImplementedError

    def GetByteSize(self, request, context):
        # TODO
        raise NotImplementedError

    def GetTopKFiles(self, request, context):
        # TODO
        raise NotImplementedError


def serve():
    """Start the insecure gRPC server and block until it is stopped."""
    data_logic.ensure_data_dir()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_service_pb2_grpc.add_WorkspaceServiceServicer_to_server(
        WorkspaceServiceServicer(), server
    )
    bound_port = server.add_insecure_port(LISTEN_ADDR)
    if bound_port == 0:
        raise RuntimeError("Failed to bind gRPC server on {}".format(LISTEN_ADDR))
    server.start()
    print("gRPC WorkspaceService listening on {}".format(LISTEN_ADDR), flush=True)

    def _handle_stop(signum, frame):
        server.stop(grace=0)

    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)
    server.wait_for_termination()
    print("Stopped.", flush=True)


if __name__ == "__main__":
    serve()
