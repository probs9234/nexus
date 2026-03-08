from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
import httpx
import uuid
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nexus_gateway')))
from core.crypto import generate_key, encrypt_data, decrypt_data
from core.sharding import split_into_shards, reassemble_shards
from core.database import init_db, save_file_metadata, get_file_metadata

app = FastAPI(title="Nexus Gateway")

# Initialize database on startup
init_db()

# List of storage node URLs (can be dynamic, but hardcoded for local demo)
NODE_URLS = [
    "http://node1:8000",
    "http://node2:8000",
    "http://node3:8000"
]

async def upload_shard_to_node(client: httpx.AsyncClient, node_url: str, shard_id: str, data: bytes):
    """Sends a single shard to a remote storage node."""
    files = {'file': (shard_id, data, 'application/octet-stream')}
    try:
        response = await client.post(f"{node_url}/shard/{shard_id}", files=files)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to upload shard {shard_id} to {node_url}: {e}")
        return False

async def download_shard_from_node(client: httpx.AsyncClient, node_url: str, shard_id: str):
    """Retrieves a single shard from a remote storage node."""
    try:
        response = await client.get(f"{node_url}/shard/{shard_id}")
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Failed to download shard {shard_id} from {node_url}: {e}")
        return None

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a file, encrypts it, shards it, and distributes it across nodes."""
    content = await file.read()
    file_id = str(uuid.uuid4())
    
    # Generate AES-256 key and encrypt
    key = generate_key()
    encrypted_data = encrypt_data(key, content)
    
    # Split into 1MB shards
    shards = split_into_shards(encrypted_data)
    shard_ids = []
    
    async with httpx.AsyncClient() as client:
        upload_tasks = []
        for i, shard_data in enumerate(shards):
            shard_id = f"{file_id}_part{i}"
            shard_ids.append(shard_id)
            
            # Simple round-robin distribution to nodes
            node_url = NODE_URLS[i % len(NODE_URLS)]
            upload_tasks.append(upload_shard_to_node(client, node_url, shard_id, shard_data))
            
        results = await asyncio.gather(*upload_tasks)
        if not all(results):
            raise HTTPException(status_code=500, detail="Failed to upload all shards to nodes.")
            
    # Save metadata
    save_file_metadata(file_id, file.filename, key, len(content), shard_ids)
    
    return {
        "message": "File uploaded and distributed successfully",
        "file_id": file_id,
        "filename": file.filename,
        "shards": len(shards)
    }

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Retrieves shards, reassembles, decrypts, and returns the original file."""
    metadata = get_file_metadata(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="File metadata not found")
        
    shard_ids = metadata["shards"]
    shards_data = []
    
    async with httpx.AsyncClient() as client:
        download_tasks = []
        for i, shard_id in enumerate(shard_ids):
            node_url = NODE_URLS[i % len(NODE_URLS)]
            download_tasks.append(download_shard_from_node(client, node_url, shard_id))
            
        results = await asyncio.gather(*download_tasks)
        
        for idx, res in enumerate(results):
            if res is None:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve shard {shard_ids[idx]} from nodes.")
            shards_data.append(res)
            
    # Reassemble and decrypt
    encrypted_data = reassemble_shards(shards_data)
    try:
        decrypted_data = decrypt_data(metadata["encryption_key"], encrypted_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to decrypt file data")
        
    return Response(
        content=decrypted_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{metadata["filename"]}"'}
    )
