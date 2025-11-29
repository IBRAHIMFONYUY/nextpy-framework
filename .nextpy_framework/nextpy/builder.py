"""
NextPy Build Optimizer - Fast builds with caching and parallel processing
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import datetime


class BuildCache:
    """Smart build caching to skip unchanged files"""
    
    def __init__(self, cache_dir: str = ".nextpy_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "build_cache.json"
        self.cache: Dict[str, str] = self._load_cache()
    
    def _load_cache(self) -> Dict[str, str]:
        if self.cache_file.exists():
            with open(self.cache_file) as f:
                return json.load(f)
        return {}
    
    def _save_cache(self) -> None:
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)
    
    def get_hash(self, file_path: str) -> str:
        """Get SHA256 hash of file"""
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def is_changed(self, file_path: str) -> bool:
        """Check if file has changed since last build"""
        current_hash = self.get_hash(file_path)
        cached_hash = self.cache.get(file_path)
        
        if cached_hash == current_hash:
            return False
        
        self.cache[file_path] = current_hash
        self._save_cache()
        return True
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()


class ParallelBuilder:
    """Build with parallel processing for faster builds"""
    
    @staticmethod
    async def build_pages(pages: List[Path], concurrency: int = 4) -> List[Dict[str, Any]]:
        """Build multiple pages in parallel"""
        results: List[Dict[str, Any]] = []
        semaphore = asyncio.Semaphore(concurrency)
        
        async def build_page(page: Path) -> Dict[str, Any]:
            async with semaphore:
                return await ParallelBuilder._build_single_page(page)
        
        tasks = [build_page(page) for page in pages]
        results = await asyncio.gather(*tasks)
        return results
    
    @staticmethod
    async def _build_single_page(page: Path) -> Dict[str, Any]:
        """Build a single page"""
        await asyncio.sleep(0.1)  # Simulate build work
        return {
            "page": str(page),
            "status": "built",
            "timestamp": datetime.now().isoformat()
        }


class BuildOptimizer:
    """Optimize bundle size and build time"""
    
    @staticmethod
    def analyze_bundle(output_dir: Path) -> Dict[str, Any]:
        """Analyze built bundle size"""
        total_size: int = 0
        files: Dict[str, int] = {}
        
        for file in output_dir.rglob("*"):
            if file.is_file():
                size = file.stat().st_size
                total_size += size
                files[str(file.relative_to(output_dir))] = size
        
        # Sort by size
        sorted_files = sorted(files.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "files": dict(sorted_files[:10]),  # Top 10 largest
            "file_count": len(files)
        }
    
    @staticmethod
    def compress_assets(output_dir: Path) -> int:
        """Compress CSS and JS files"""
        import gzip
        compressed_count: int = 0
        
        for file in list(output_dir.rglob("*.js")) + list(output_dir.rglob("*.css")):
            if file.is_file():
                with open(file, "rb") as f_in:
                    content = f_in.read()
                with gzip.open(f"{file}.gz", "wb") as f_out:
                    f_out.write(content)
                compressed_count += 1
        
        return compressed_count
