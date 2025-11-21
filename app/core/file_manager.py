import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class FileManager:
    @staticmethod
    def save_json(data: Dict[str, Any], filename: str) -> bool:
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_json(filename: str) -> Optional[Dict[str, Any]]:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    @staticmethod
    def save_html(content: str, filename: str) -> bool:
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    def save_markdown(content: str, filename: str) -> bool:
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False
