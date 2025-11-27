import asyncio
import subprocess
from typing import Dict, Any, Optional
import tempfile
import os
from pathlib import Path
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class CodeExecutor:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.supported_languages = {
            "python": {"ext": ".py", "cmd": "python"},
            "javascript": {"ext": ".js", "cmd": "node"},
            "bash": {"ext": ".sh", "cmd": "bash"},
            "powershell": {"ext": ".ps1", "cmd": "powershell"}
        }
    
    async def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        if language not in self.supported_languages:
            return {"error": f"Unsupported language: {language}"}
        
        lang_config = self.supported_languages[language]
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=lang_config["ext"],
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = await asyncio.wait_for(
                self._run_code(lang_config["cmd"], temp_file),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            return {"error": "Execution timeout", "timeout": self.timeout}
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def _run_code(self, cmd: str, file_path: str) -> Dict[str, Any]:
        try:
            process = await asyncio.create_subprocess_exec(
                cmd, file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def execute_shell(self, command: str) -> Dict[str, Any]:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.communicate()
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
        except Exception as e:
            return {"error": str(e)}
