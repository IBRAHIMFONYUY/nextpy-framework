"""
NextPy File Upload Utilities
Handle file uploads with validation and storage
"""

import os
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import shutil


UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def upload_file(
    file: UploadFile,
    directory: str = "general",
    max_size: int = MAX_FILE_SIZE,
) -> Optional[str]:
    """Upload file with validation"""
    
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not allowed")
    
    # Create upload directory
    upload_path = UPLOAD_DIR / directory
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_path / file.filename
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            if len(content) > max_size:
                raise ValueError(f"File too large (max {max_size} bytes)")
            f.write(content)
        
        return str(file_path)
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise e


async def delete_file(file_path: str) -> bool:
    """Delete uploaded file"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception:
        return False


def get_upload_url(file_path: str) -> str:
    """Get public URL for uploaded file"""
    return f"/uploads/{file_path}"
