import asyncio
import httpx
import uvicorn
import multiprocessing
import time
import os
import shutil

# Start up 3 nodes and 1 gateway locally on different ports
def start_node(port):
    os.environ["STORAGE_DIR"] = f"nexus_data/node_{port}"
    from nexus_node.main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

def start_gateway():
    from nexus_gateway.main import app
    # Override node URLs for local test
    import nexus_gateway.main
    nexus_gateway.main.NODE_URLS = [
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8002",
        "http://127.0.0.1:8003"
    ]
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

async def test_upload_download():
    # Wait for servers to start
    print("[*] Waiting 8 seconds for 4 Uvicorn servers to start...")
    time.sleep(8)
    
    # Create test file
    test_content = b"Hello, this is a highly confidential document stored on Nexus distributed cloud storage. " * 50000 # Make it approx 4MB
    with open("test.txt", "wb") as f:
        f.write(test_content)
        
    print(f"[*] Created test file of size {len(test_content)} bytes")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Upload
        print("[*] Uploading file to gateway...")
        with open("test.txt", "rb") as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            response = await client.post("http://127.0.0.1:8000/upload", files=files)
            
        if response.status_code != 200:
            print(f"[!] Upload failed: {response.text}")
            return
            
        data = response.json()
        file_id = data["file_id"]
        print(f"[*] Upload successful! File ID: {file_id}. Shards: {data['shards']}")
        
        # 2. Verify Shards exist on disk
        print("\n[*] Verifying shards on local simulated nodes (should be distributed round-robin):")
        for i in range(1, 4):
            port = 8000 + i
            shard_dir = f"nexus_data/node_{port}"
            if os.path.exists(shard_dir):
                shards = os.listdir(shard_dir)
                print(f"  - Node {port} has {len(shards)} shards: {shards}")
                
        # 3. Download
        print("\n[*] Downloading file from gateway...")
        response = await client.get(f"http://127.0.0.1:8000/download/{file_id}")
        if response.status_code != 200:
            print(f"[!] Download failed: {response.text}")
            return
            
        downloaded_content = response.content
        print(f"[*] Download complete. Size: {len(downloaded_content)} bytes")
        
        if downloaded_content == test_content:
            print("[*] SUCCESS! Downloaded content matches original perfectly.")
        else:
            print("[!] FAILURE! Downloaded content does NOT match original.")

if __name__ == "__main__":
    # Clean up old data
    if os.path.exists("nexus_data"):
        shutil.rmtree("nexus_data")
    if os.path.exists("nexus_metadata.db"):
        os.remove("nexus_metadata.db")
        
    # Start processes
    processes = []
    
    p_gateway = multiprocessing.Process(target=start_gateway)
    processes.append(p_gateway)
    p_gateway.start()
    
    for port in [8001, 8002, 8003]:
        p = multiprocessing.Process(target=start_node, args=(port,))
        processes.append(p)
        p.start()
        
    try:
        asyncio.run(test_upload_download())
    finally:
        for p in processes:
            p.terminate()
            p.join()
        if os.path.exists("test.txt"):
            os.remove("test.txt")
