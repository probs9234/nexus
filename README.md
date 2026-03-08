# Nexus - Distributed Cloud Storage

A secure, decentralized file storage system built on a microservices architecture. It utilizes sharding and AES-256 encryption to split and store files across multiple peer nodes, ensuring high availability and zero-knowledge privacy.

## Features Implemented
1. **Zero-Knowledge Encryption**: All files uploaded via the `nexus_gateway` are instantly encrypted using AES-256 GCM in memory before ever touching the disk.
2. **File Sharding**: Encrypted blobs are split into fixed 1MB chunks to distribute storage weight evenly.
3. **Multi-Node Distribution**: Shards are distributed round-robin across simulated `nexus_node` independent instances.
4. **Resilient Reassembly**: The gateway downloads shards sequentially from disparate nodes, reassembles the binary blob, and decrypts the original file safely.
5. **Containerization**: Configured `docker-compose.yml` to spin up 3 storage nodes and 1 orchestration gateway instantly.

## Architecture Architecture

- **Gateway Service (`nexus_gateway`)**: Exposes a REST API (`POST /upload`, `GET /download/{file_id}`). Receives files from users, encrypts them using AES-256, splits them into 1MB shards, and distributes them to storage nodes. Tracks metadata in SQLite.
- **Storage Node Service (`nexus_node`)**: A lightweight peer node microservice that simply accepts encrypted bytes and stores them. Has no knowledge of the original file contents.

## Running Locally

Requirements:
- Docker and Docker Compose

```bash
# Clone the repository
git clone https://github.com/probs9234/nexus.git
cd nexus

# Spin up the infrastructure (1 Gateway, 3 Nodes)
docker-compose up -d --build
```

Then visit `http://localhost:8000/docs` to use the FastAPI Swagger UI to natively test file uploads and downloads.

## Running E2E Test (Python)

If you'd like to run the end-to-end Python test without Docker:

```bash
# Install dependencies
pip install fastapi uvicorn httpx cryptography python-multipart

# Run the test
python test_e2e.py
```
This will spin up local servers on ports 8000, 8001, 8002, and 8003, upload a 4.5MB test file, verify proper distribution, and download/verify the decrypted file.
