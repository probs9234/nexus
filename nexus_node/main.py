from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
import os

app = FastAPI(title="Nexus Storage Node")

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.post("/shard/{shard_id}")
async def upload_shard(shard_id: str, file: UploadFile = File(...)):
    """Stores an encrypted shard on disk."""
    file_path = os.path.join(STORAGE_DIR, shard_id)
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    return {"message": "Shard saved successfully", "shard_id": shard_id, "size": len(content)}

@app.get("/shard/{shard_id}")
async def download_shard(shard_id: str):
    """Retrieves an encrypted shard from disk."""
    file_path = os.path.join(STORAGE_DIR, shard_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Shard not found")
        
    with open(file_path, "rb") as f:
        content = f.read()
        
    return Response(content=content, media_type="application/octet-stream")

@app.get("/health")
def health_check():
    return {"status": "ok"}
