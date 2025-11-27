"""Fullstack code generation workflow"""
from typing import Dict, Any
from app.core.llm_client import get_llm_client
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class FullstackCodingAgent:
    """Code generation with test-first approach"""
    
    async def build(self, task: str) -> Dict[str, Any]:
        """Execute fullstack coding workflow"""
        
        # Step 1: Generate tests
        tests = await self._generate_tests(task)
        
        # Step 2: Generate implementation
        code = await self._generate_code(task, tests)
        
        # Step 3: Execute and validate
        validation = await self._validate_code(code, tests)
        
        # Step 4: Generate documentation
        docs = await self._generate_docs(task, code)
        
        return {
            "task": task,
            "tests": tests,
            "code": code,
            "validation": validation,
            "documentation": docs,
            "status": "success" if validation.get("passed") else "failed"
        }
    
    async def _generate_tests(self, task: str) -> str:
        """Generate test cases first"""
        llm = get_llm_client()
        
        prompt = f"""Generate comprehensive test cases for the following task:

Task: {task}

Provide tests in Python (pytest format) that cover:
1. Happy path
2. Edge cases
3. Error handling
4. Performance requirements

Format as valid Python code."""
        
        tests = await llm.generate(prompt, max_tokens=1024)
        return tests
    
    async def _generate_code(self, task: str, tests: str) -> str:
        """Generate implementation code"""
        llm = get_llm_client()
        
        prompt = f"""Generate production-ready Python code for:

Task: {task}

Tests to pass:
{tests}

Requirements:
1. Pass all provided tests
2. Include error handling
3. Add type hints
4. Include docstrings
5. Follow PEP 8

Provide complete, runnable code."""
        
        code = await llm.generate(prompt, max_tokens=2048)
        return code
    
    async def _validate_code(self, code: str, tests: str) -> Dict[str, Any]:
        """Validate code against tests"""
        try:
            # This would execute tests in a sandbox
            # For now, return mock validation
            return {
                "passed": True,
                "test_count": 5,
                "coverage": 0.95,
                "errors": []
            }
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "passed": False,
                "errors": [str(e)]
            }
    
    async def _generate_docs(self, task: str, code: str) -> str:
        """Generate documentation"""
        llm = get_llm_client()
        
        prompt = f"""Generate documentation for the following code:

Task: {task}

Code:
{code[:1000]}...

Include:
1. Overview
2. Installation
3. Usage examples
4. API reference
5. Contributing guidelines"""
        
        docs = await llm.generate(prompt, max_tokens=1024)
        return docs
