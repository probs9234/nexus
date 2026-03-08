import os
from typing import List

CHUNK_SIZE = 1024 * 1024  # 1 MB

def split_into_shards(file_data: bytes, chunk_size: int = CHUNK_SIZE) -> List[bytes]:
    """Splits a single byte array into a list of fixed-size chunks."""
    return [file_data[i:i+chunk_size] for i in range(0, len(file_data), chunk_size)]

def reassemble_shards(shards: List[bytes]) -> bytes:
    """Reassembles a list of byte chunks back into a single byte array."""
    return b"".join(shards)
