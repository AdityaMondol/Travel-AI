from typing import List, Dict, Any, Tuple
import logging
from backend.utils.nim_client import nim_client

logger = logging.getLogger(__name__)

class SafetyService:
    def __init__(self):
        self.disallowed_topics = [
            "illegal acts", "harmful content", "doxxing", "malware generation", 
            "financial fraud", "unauthorized access", "hate speech"
        ]

    async def validate_intent(self, objective: str) -> Tuple[bool, str]:
        """
        Validates the user objective against safety policies using an LLM.
        Returns (is_safe, reason).
        """
        prompt = f"""
        Analyze the following user objective for safety violations.
        Objective: "{objective}"
        
        Policies:
        - No illegal acts or assistance with crime.
        - No generation of malware or exploit code.
        - No doxxing or PII extraction.
        - No financial fraud or scams.
        - No hate speech or harassment.
        
        Is this objective safe to proceed? Answer strictly YES or NO, followed by a brief reason.
        Format: YES/NO: Reason
        """
        
        try:
            response = await nim_client.chat_completion(
                model="meta/llama3-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            content = response["choices"][0]["message"]["content"].strip()
            
            if content.upper().startswith("NO"):
                logger.warning(f"Safety violation detected: {content}")
                return False, content
            
            return True, "Safe"
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            # Fail safe
            return False, "Safety check failed due to system error."

    async def scan_pii(self, text: str) -> bool:
        """
        Scans text for PII. Returns True if PII is detected.
        Placeholder for more advanced PII scanning logic.
        """
        # Simple keyword check for demonstration
        pii_keywords = ["ssn", "credit card", "password", "private key"]
        if any(keyword in text.lower() for keyword in pii_keywords):
            return True
        return False

safety_service = SafetyService()
