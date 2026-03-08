<div align="center">
  <h1>🌌 Nexus Storage Node</h1>
  <p><i>A secure, decentralized file storage system built on a microservices architecture.</i></p>

  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
  [![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## ✨ Features Implemented

<details>
<summary><b>1. Zero-Knowledge Encryption 🔒</b></summary>
All files uploaded via the <code>nexus_gateway</code> are instantly encrypted using AES-256 GCM in memory before ever touching the disk.
</details>

<details>
<summary><b>2. File Sharding ✂️</b></summary>
Encrypted blobs are split into fixed 1MB chunks to distribute storage weight evenly across the network.
</details>

<details>
<summary><b>3. Multi-Node Distribution 🌐</b></summary>
Shards are distributed round-robin across simulated <code>nexus_node</code> independent instances seamlessly.
</details>

<details>
<summary><b>4. Resilient Reassembly 🧩</b></summary>
The gateway downloads shards sequentially from disparate nodes, reassembles the binary blob, and decrypts the original file safely on demand.
</details>

<details>
<summary><b>5. Containerization 🐳</b></summary>
Configured <code>docker-compose.yml</code> to spin up 3 storage nodes and 1 orchestration gateway instantly with a single command.
</details>

---

## 🏗️ Architecture

- 🛡️ **Gateway Service (`nexus_gateway`)**: Exposes a REST API (`POST /upload`, `GET /download/{file_id}`). Receives files from users, encrypts them using AES-256, splits them into 1MB shards, and distributes them to storage nodes. Tracks metadata in SQLite.
- 💾 **Storage Node Service (`nexus_node`)**: A lightweight peer node microservice that simply accepts encrypted bytes and stores them. Has no knowledge of the original file contents.

---

## 🚀 Running Locally

You'll need docker and docker-compose installed!

<details>
<summary><b>🐳 Quick Start (Docker)</b></summary>

```bash
# Clone the repository
git clone https://github.com/probs9234/nexus.git
cd nexus

# Spin up the infrastructure (1 Gateway, 3 Nodes)
docker-compose up -d --build
```

Then visit `http://localhost:8000/docs` to use the interactive FastAPI Swagger UI to test file uploads and downloads.
</details>

<details>
<summary><b>🐍 Bare-Metal Testing (Python)</b></summary>
If you'd like to run the end-to-end Python test without Docker:

```bash
# Install dependencies
pip install fastapi uvicorn httpx cryptography python-multipart

# Run the test
python test_e2e.py
```
This will automatically spin up 4 local background uvicorn servers (Gateway + 3 Nodes) and run a full end-to-end simulation.
</details>

---
<div align="center">
  <i>Built with ❤️ using FastAPI | Made by <b>probs</b></i>
</div>
