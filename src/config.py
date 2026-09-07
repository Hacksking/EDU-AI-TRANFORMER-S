import os
from pathlib import Path

class ChunkerConfig:
    """Configuration settings for the Semantic Chunking Pipeline."""
    
    def __init__(
        self,
        input_dir: str = "json",
        output_dir: str = "chunks",
        logs_dir: str = "logs",
        chunk_size: int = 700,
        chunk_overlap: int = 100,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1200
    ):
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.logs_dir = Path(logs_dir).resolve()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
