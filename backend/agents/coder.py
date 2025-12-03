from typing import Dict, Any, Tuple
from backend.agents.base import BaseAgent
import subprocess
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class CoderAgent(BaseAgent):
    def __init__(self, job_id: str):
        super().__init__("coder", job_id)

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        spec = input_data.get("instruction")
        self.log_activity("coding_started", {"spec": spec})

        # 1. Generate Code & Tests
        prompt = f"""
        You are an expert Python developer.
        Task: {spec}
        
        Write a complete Python script that implements the task.
        Include a main block or test function to verify correctness.
        The code must be self-contained.
        
        Return ONLY the python code block.
        """
        
        code_response = await self.call_llm([{"role": "user", "content": prompt}], temperature=0.2)
        code = self._extract_code(code_response)
        
        # 2. Execute Code (Sandbox - Local Subprocess)
        # WARNING: In a real production system, use a secure container (Docker/Firecracker).
        # Here we run locally as per instructions "normal Python environment".
        
        success, output = self._execute_code(code)
        
        if not success:
            self.log_activity("execution_failed", {"output": output})
            # Retry logic could go here (feed error back to LLM)
            return {"status": "failed", "code": code, "error": output}
            
        self.log_activity("execution_success", {"output": output})
        return {"status": "success", "code": code, "output": output}

    def _extract_code(self, text: str) -> str:
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text

    def _execute_code(self, code: str) -> Tuple[bool, str]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
            
        try:
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=30 # Safety timeout
            )
            os.unlink(temp_path)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return False, str(e)
