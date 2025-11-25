from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from app.core.llm_client import LLMClient
from app.tools.code_executor import CodeExecutor
from app.tools.file_operations import FileOperations
from app.core.logger import setup_logger
import asyncio

logger = setup_logger(__name__)

class CodingState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task: str
    architecture: str
    code_files: dict
    tests: dict
    execution_results: dict
    documentation: str
    iteration: int
    errors: list

class FullstackCodingAgent:
    def __init__(self):
        self.llm = LLMClient(provider="nvidia", model="mistralai/codestral-22b-instruct-v0.1")
        self.architect_llm = LLMClient(provider="nvidia", model="meta/llama-3.1-405b-instruct")
        self.executor = CodeExecutor()
        self.file_ops = FileOperations()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(CodingState)
        
        workflow.add_node("architect", self.design_architecture)
        workflow.add_node("generate_backend", self.generate_backend)
        workflow.add_node("generate_frontend", self.generate_frontend)
        workflow.add_node("generate_tests", self.generate_tests)
        workflow.add_node("execute_tests", self.execute_tests)
        workflow.add_node("fix_errors", self.fix_errors)
        workflow.add_node("generate_docs", self.generate_documentation)
        workflow.add_node("review_code", self.review_code)
        
        workflow.set_entry_point("architect")
        
        workflow.add_edge("architect", "generate_backend")
        workflow.add_edge("generate_backend", "generate_frontend")
        workflow.add_edge("generate_frontend", "generate_tests")
        workflow.add_edge("generate_tests", "execute_tests")
        
        workflow.add_conditional_edges(
            "execute_tests",
            self.check_tests,
            {
                "fix": "fix_errors",
                "continue": "generate_docs"
            }
        )
        
        workflow.add_edge("fix_errors", "execute_tests")
        workflow.add_edge("generate_docs", "review_code")
        
        workflow.add_conditional_edges(
            "review_code",
            self.should_iterate,
            {
                "iterate": "architect",
                "end": END
            }
        )
        
        return workflow.compile()
    
    async def design_architecture(self, state: CodingState) -> CodingState:
        task = state["task"]
        
        arch_prompt = f"""
Design a complete fullstack architecture for:

Task: {task}

Provide:
1. Technology stack (backend, frontend, database)
2. Project structure (folders, files)
3. API endpoints design
4. Data models
5. Frontend components
6. Security considerations
7. Deployment strategy

Be specific and production-ready."""

        architecture = await asyncio.to_thread(self.architect_llm.generate, arch_prompt, 0.7)
        
        state["architecture"] = architecture
        state["messages"].append(AIMessage(content=f"Architecture designed"))
        return state
    
    async def generate_backend(self, state: CodingState) -> CodingState:
        backend_prompt = f"""
Generate complete backend code for:

Task: {state['task']}
Architecture: {state['architecture']}

Generate:
1. FastAPI application with all endpoints
2. Database models (SQLAlchemy)
3. Business logic
4. Authentication/Authorization
5. Error handling
6. Configuration

Provide complete, production-ready code for each file.
Format: filename.py followed by code block."""

        backend_code = await asyncio.to_thread(self.llm.generate, backend_prompt, 0.2)
        
        files = self._parse_code_blocks(backend_code)
        state["code_files"] = {**state.get("code_files", {}), **files}
        
        for filename, content in files.items():
            await self.file_ops.write_file(f"backend/{filename}", content)
        
        state["messages"].append(AIMessage(content=f"Generated {len(files)} backend files"))
        return state
    
    async def generate_frontend(self, state: CodingState) -> CodingState:
        frontend_prompt = f"""
Generate complete frontend code for:

Task: {state['task']}
Architecture: {state['architecture']}
Backend API: {state['code_files']}

Generate:
1. HTML structure
2. Vanilla JavaScript (no frameworks)
3. TailwindCSS styling
4. API integration
5. State management
6. Error handling

Provide complete, production-ready code.
Format: filename.html/js followed by code block."""

        frontend_code = await asyncio.to_thread(self.llm.generate, frontend_prompt, 0.2)
        
        files = self._parse_code_blocks(frontend_code)
        state["code_files"] = {**state.get("code_files", {}), **files}
        
        for filename, content in files.items():
            await self.file_ops.write_file(f"frontend/{filename}", content)
        
        state["messages"].append(AIMessage(content=f"Generated {len(files)} frontend files"))
        return state
    
    async def generate_tests(self, state: CodingState) -> CodingState:
        test_prompt = f"""
Generate comprehensive tests for:

Code: {state['code_files']}

Generate:
1. Unit tests for all functions
2. Integration tests for API endpoints
3. Frontend tests
4. Edge cases
5. Error scenarios

Use pytest. Provide complete test files.
Format: test_filename.py followed by code block."""

        test_code = await asyncio.to_thread(self.llm.generate, test_prompt, 0.2)
        
        tests = self._parse_code_blocks(test_code)
        state["tests"] = tests
        
        for filename, content in tests.items():
            await self.file_ops.write_file(f"tests/{filename}", content)
        
        state["messages"].append(AIMessage(content=f"Generated {len(tests)} test files"))
        return state
    
    async def execute_tests(self, state: CodingState) -> CodingState:
        results = {}
        errors = []
        
        for test_file, test_code in state["tests"].items():
            result = await self.executor.execute(test_code, "python")
            results[test_file] = result
            
            if result.get("status") == "error" or result.get("returncode", 0) != 0:
                errors.append({
                    "file": test_file,
                    "error": result.get("stderr", "Unknown error")
                })
        
        state["execution_results"] = results
        state["errors"] = errors
        state["messages"].append(AIMessage(content=f"Executed {len(results)} tests, {len(errors)} failures"))
        return state
    
    async def fix_errors(self, state: CodingState) -> CodingState:
        errors = state["errors"]
        
        fix_prompt = f"""
Fix these errors in the code:

Errors: {errors}

Original code: {state['code_files']}

Provide corrected code for each file with errors.
Format: filename followed by corrected code block."""

        fixed_code = await asyncio.to_thread(self.llm.generate, fix_prompt, 0.2)
        
        fixes = self._parse_code_blocks(fixed_code)
        state["code_files"].update(fixes)
        
        for filename, content in fixes.items():
            path = f"backend/{filename}" if filename.endswith('.py') else f"frontend/{filename}"
            await self.file_ops.write_file(path, content)
        
        state["iteration"] = state.get("iteration", 0) + 1
        state["messages"].append(AIMessage(content=f"Fixed {len(fixes)} files"))
        return state
    
    async def generate_documentation(self, state: CodingState) -> CodingState:
        doc_prompt = f"""
Generate comprehensive documentation for:

Task: {state['task']}
Architecture: {state['architecture']}
Code: {state['code_files']}

Include:
1. README with setup instructions
2. API documentation
3. Architecture overview
4. Deployment guide
5. Usage examples
6. Troubleshooting

Make it professional and complete."""

        docs = await asyncio.to_thread(self.architect_llm.generate, doc_prompt, 0.6)
        
        state["documentation"] = docs
        await self.file_ops.write_file("README.md", docs)
        
        state["messages"].append(AIMessage(content="Documentation generated"))
        return state
    
    async def review_code(self, state: CodingState) -> CodingState:
        review_prompt = f"""
Perform a thorough code review:

Code: {state['code_files']}
Tests: {state['execution_results']}

Evaluate:
1. Code quality (0-10)
2. Security (0-10)
3. Performance (0-10)
4. Test coverage (0-10)
5. Documentation (0-10)

Identify critical issues and improvements needed."""

        review = await asyncio.to_thread(self.architect_llm.generate, review_prompt, 0.3)
        
        state["messages"].append(AIMessage(content=f"Code Review:\n{review}"))
        return state
    
    def check_tests(self, state: CodingState) -> str:
        if state["errors"] and state.get("iteration", 0) < 3:
            return "fix"
        return "continue"
    
    def should_iterate(self, state: CodingState) -> str:
        if state.get("iteration", 0) >= 2:
            return "end"
        
        last_review = state["messages"][-1].content
        scores = [int(s) for s in last_review.split() if s.isdigit()]
        
        if scores and min(scores) < 7:
            return "iterate"
        
        return "end"
    
    def _parse_code_blocks(self, text: str) -> dict:
        files = {}
        lines = text.split('\n')
        current_file = None
        current_code = []
        in_code_block = False
        
        for line in lines:
            if line.strip().endswith(('.py', '.js', '.html', '.css', '.json')):
                if current_file and current_code:
                    files[current_file] = '\n'.join(current_code)
                current_file = line.strip().split()[-1]
                current_code = []
                in_code_block = False
            elif line.strip().startswith('```'):
                in_code_block = not in_code_block
            elif in_code_block and current_file:
                current_code.append(line)
        
        if current_file and current_code:
            files[current_file] = '\n'.join(current_code)
        
        return files
    
    async def build(self, task: str) -> dict:
        initial_state = CodingState(
            messages=[HumanMessage(content=task)],
            task=task,
            architecture="",
            code_files={},
            tests={},
            execution_results={},
            documentation="",
            iteration=0,
            errors=[]
        )
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            return {
                "status": "success",
                "files": final_state["code_files"],
                "tests": final_state["tests"],
                "documentation": final_state["documentation"],
                "test_results": final_state["execution_results"]
            }
        except Exception as e:
            logger.error(f"Coding workflow failed: {e}")
            return {"status": "error", "error": str(e)}
