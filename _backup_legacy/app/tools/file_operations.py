import asyncio
from typing import Dict, Any, List
from pathlib import Path
import shutil
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class FileOperations:
    def __init__(self, workspace: str = "./workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        try:
            file_path = self.workspace / path
            content = await asyncio.to_thread(file_path.read_text)
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        try:
            file_path = self.workspace / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(file_path.write_text, content)
            return {"status": "success", "path": str(file_path)}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def list_files(self, path: str = ".") -> Dict[str, Any]:
        try:
            dir_path = self.workspace / path
            files = await asyncio.to_thread(list, dir_path.iterdir())
            return {
                "status": "success",
                "files": [
                    {
                        "name": f.name,
                        "type": "dir" if f.is_dir() else "file",
                        "size": f.stat().st_size if f.is_file() else 0
                    }
                    for f in files
                ]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def delete_file(self, path: str) -> Dict[str, Any]:
        try:
            file_path = self.workspace / path
            if file_path.is_dir():
                await asyncio.to_thread(shutil.rmtree, file_path)
            else:
                await asyncio.to_thread(file_path.unlink)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def create_directory(self, path: str) -> Dict[str, Any]:
        try:
            dir_path = self.workspace / path
            await asyncio.to_thread(dir_path.mkdir, parents=True, exist_ok=True)
            return {"status": "success", "path": str(dir_path)}
        except Exception as e:
            return {"status": "error", "error": str(e)}
