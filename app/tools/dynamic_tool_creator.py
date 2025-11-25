import asyncio
from typing import Dict, Any, Callable
import inspect
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class DynamicToolCreator:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def create_tool_from_description(self, name: str, description: str, llm_client) -> Callable:
        creation_prompt = f"""
Generate Python code for a tool with this specification:

Name: {name}
Description: {description}

Requirements:
1. Function must be async
2. Must have type hints
3. Must handle errors gracefully
4. Must return Dict[str, Any]
5. Must be self-contained

Provide ONLY the function code, no explanations:

```python
async def {name}(...) -> Dict[str, Any]:
    # implementation
```
"""

        code = await asyncio.to_thread(llm_client.generate, creation_prompt, 0.2)
        
        code = code.strip()
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        try:
            local_scope = {}
            exec(code, {"asyncio": asyncio, "Dict": Dict, "Any": Any}, local_scope)
            
            tool_func = local_scope.get(name)
            if not tool_func:
                raise ValueError(f"Function {name} not found in generated code")
            
            self.tools[name] = tool_func
            self.tool_metadata[name] = {
                "description": description,
                "code": code,
                "created_at": asyncio.get_event_loop().time()
            }
            
            logger.info(f"Created dynamic tool: {name}")
            return tool_func
            
        except Exception as e:
            logger.error(f"Failed to create tool {name}: {e}")
            raise
    
    def register_tool(self, name: str, func: Callable, description: str = ""):
        self.tools[name] = func
        self.tool_metadata[name] = {
            "description": description or func.__doc__ or "",
            "signature": str(inspect.signature(func)),
            "is_async": inspect.iscoroutinefunction(func)
        }
        logger.info(f"Registered tool: {name}")
    
    async def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        if name not in self.tools:
            return {"error": f"Tool {name} not found"}
        
        tool = self.tools[name]
        
        try:
            if inspect.iscoroutinefunction(tool):
                result = await tool(**kwargs)
            else:
                result = await asyncio.to_thread(tool, **kwargs)
            
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "metadata": meta
            }
            for name, meta in self.tool_metadata.items()
        ]
    
    def remove_tool(self, name: str):
        if name in self.tools:
            del self.tools[name]
            del self.tool_metadata[name]
            logger.info(f"Removed tool: {name}")
