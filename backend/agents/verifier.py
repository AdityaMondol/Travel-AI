from typing import Dict, Any
from backend.agents.base import BaseAgent

class VerifierAgent(BaseAgent):
    def __init__(self, job_id: str):
        super().__init__("verifier", job_id)

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        content_to_verify = input_data.get("content")
        context = input_data.get("context", "")
        
        self.log_activity("verification_started", {"context": context})

        prompt = f"""
        Verify the following content for accuracy, logical consistency, and safety.
        Context: {context}
        Content: {content_to_verify}
        
        Identify any:
        1. Factual errors (hallucinations).
        2. Logical inconsistencies.
        3. Safety violations.
        
        Return a JSON object:
        {{
            "is_valid": boolean,
            "issues": ["list of issues"],
            "confidence_score": 0.0-1.0
        }}
        """
        
        response = await self.call_llm([{"role": "user", "content": prompt}], temperature=0.1)
        
        # Simple parsing (in production use a robust JSON parser)
        import json
        try:
            clean_response = response.replace("```json", "").replace("```", "").strip()
            verification_result = json.loads(clean_response)
        except:
            verification_result = {"is_valid": False, "issues": ["Failed to parse verification result"], "confidence_score": 0.0}

        self.log_activity("verification_complete", verification_result)
        return verification_result
