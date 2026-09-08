# Lab 1 — gRPC workspace monitor

## 1. Overview

Lab 1 implements a terminal dashboard that monitors workspace usage under `data/`.

The dashboard is a gRPC client. It periodically queries a gRPC backend and prints live stats so you can watch how the workspace is being used:

+ how many files are stored (`GetFileCount`)
+ how many lines of text there are in total (`GetLineCount`)
+ how many bytes those files occupy on disk (`GetByteSize`)
+ which files use the most space (`GetTopKFiles`)

From an implementation perspective, the client talks to the gRPC service, and the service reads stats :

```
grpc_client.py --gRPC stats--> grpc_service.py ----> data_logic.py --read--> data/*
```

Your task is to fill in the TODOs in `grpc_service.py`, i.e. to implement the query RPCs.

We have implemented the others for you:
+ The terminal dashboard client (`frontend/grpc_client.py`).
+ The protobuf contract (`backend/file_service.proto`).
+ The data layer (`backend/data_logic.py`).
  - **NOTE**: if you reuse the helpers in that file, it will not take much code to finish the tasks.
  - Feel free if you want have use your own implementation (it should be included in `grpc_service.py`).

## 2. Evaluation

The evaluation will be based on two perspectives (Section 6 will help you with this):
+ Whether the four RPC services work correctly.
+ You may take care of the special conditions, such as:
  - empty `data/`
  - edge input cases, e.g. `k<=0`.

You can test your code based on:
+ Observing the the terminal dashboard (`frontend/grpc_client.py`), while
+ manually change the content of `data/` and observe the changes on dashboard.

We will test your code in a similar way, but using a test script.

## 3. File structure

```
Lab1/
├── frontend/
│   └── grpc_client.py      # terminal dashboard (provided)
├── backend/
│   ├── data_logic.py       # shared disk layer (provided)
│   ├── file_service.proto  # protobuf contract (provided)
│   └── grpc_service.py     # gRPC on :50051 — fill in the TODOs
├── data/                   # shared store
└── requirements.txt
```

After you generate stubs (see Setup), `backend/` will also contain:

```
file_service_pb2.py
file_service_pb2_grpc.py
```

## 4. Setup

```bash
pip install -r requirements.txt
```

The proto file is provided. You must generate the Python stubs yourself from `backend/`:

```bash
cd backend
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_service.proto
```

This creates `file_service_pb2.py` and `file_service_pb2_grpc.py` next to the `.proto` file. Both `grpc_service.py` and `grpc_client.py` import them.

## 5. Run

Use two separate terminals:

The following command starts the gRPC backend:

```bash
python3 backend/grpc_service.py
```

The following command starts the terminal dashboard:

```bash
python3 frontend/grpc_client.py
```

The dashboard polls every 5 seconds and reprints file count, line count, byte size, and the top-5 largest files.

If a previous run left a port busy:

On Mac/UNIX
```bash
lsof -tiTCP:50051 -sTCP:LISTEN | xargs kill
```

On Windows
```bash
netstat -ano | findstr :50051
taskkill /PID <pid it shows> /F
```

## 6. TODO

Fill in the `# TODO` RPC bodies in `backend/grpc_service.py`:

| RPC | Function |
|-----|----------|
| `GetFileCount` | Number of regular files in `data/` |
| `GetLineCount` | Total lines (`str.splitlines()`; skip non-UTF-8 files) |
| `GetByteSize` | Sum of on-disk sizes in bytes |
| `GetTopKFiles` | Up to `k` largest files by on-disk size (largest first), each with `name` and `size` |

The protocol of the Request / response is declared in `file_service.proto`.

| RPC | Request | Response |
|-----|---------|----------|
| count RPCs | empty `StatsRequest` | `CountResponse { int64 value }` |
| `GetTopKFiles` | `TopKRequest { int32 k }` | `TopKResponse { repeated FileSize files }` where `FileSize` is `{ string name, int64 size }` |

Notes:
+ Empty `data/` should return zeros / an empty `files` list, not an error.
+ For `GetTopKFiles`: if `k <= 0`, return an empty list; if `k` is larger than the file count, return all files. Sort by size descending; break ties by filename ascending.

## 7. Ports

| Service | Bind | URL |
|---------|------|-----|
| gRPC | `127.0.0.1:50051` | `127.0.0.1:50051` (terminal client only) |
