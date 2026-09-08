"""
Terminal gRPC monitor for Online Code Explorer.

This is not a web page. It talks to backend/grpc_service.py over gRPC
(127.0.0.1:50051) and never calls REST or reads data/ itself.

Start the gRPC server first:
    python3 backend/grpc_service.py

Then, from the project root:
    python3 frontend/grpc_client.py

Polls workspace stats every 5 seconds and replaces the previous terminal
snapshot: file count, line count, byte size, and the top-K largest files.
"""

import os
import sys
import time

import grpc

_FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_FRONTEND_DIR)
_BACKEND_DIR = os.path.join(_PROJECT_ROOT, "backend")
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

import file_service_pb2
import file_service_pb2_grpc

GRPC_TARGET = "127.0.0.1:50051"
POLL_SECONDS = 5
TOP_K = 5


def _clear_screen():
    """Replace the previous snapshot instead of appending a log."""
    # Cursor / VS Code often ignore a bare \\033[2J, so the monitor looks like
    # a growing log. `clear`/`cls` plus 3J (drop scrollback) actually resets it.
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()


def _fetch_stats(stub):
    """Query the read-only RPCs. Returns (files, lines, bytes, top_files)."""
    empty = file_service_pb2.StatsRequest()
    files = stub.GetFileCount(empty).value
    lines = stub.GetLineCount(empty).value
    size = stub.GetByteSize(empty).value
    top = stub.GetTopKFiles(file_service_pb2.TopKRequest(k=TOP_K)).files
    return files, lines, size, top


def _print_stats(files, lines, size, top_files):
    print("Online Code Explorer — workspace status")
    print("  files:  {}".format(files))
    print("  lines:  {}".format(lines))
    print("  bytes:  {}".format(size))
    print("  top {}:".format(TOP_K))
    if not top_files:
        print("    (none)")
    else:
        for index, item in enumerate(top_files, start=1):
            print("    {}. {}  ({} bytes)".format(index, item.name, item.size))
    print("  (refresh every {}s, Ctrl+C to quit)".format(POLL_SECONDS))
    sys.stdout.flush()


def _print_unreachable():
    _clear_screen()
    print("Cannot reach gRPC server at {}".format(GRPC_TARGET))
    print("Start it with: python3 backend/grpc_service.py")
    print("Retrying every {}s (Ctrl+C to quit)".format(POLL_SECONDS))
    sys.stdout.flush()


def run():
    channel = grpc.insecure_channel(GRPC_TARGET)
    stub = file_service_pb2_grpc.WorkspaceServiceStub(channel)

    try:
        while True:
            try:
                files, lines, size, top_files = _fetch_stats(stub)
            except grpc.RpcError:
                _print_unreachable()
            else:
                _clear_screen()
                _print_stats(files, lines, size, top_files)
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("")
        print("Stopped.")


if __name__ == "__main__":
    run()
