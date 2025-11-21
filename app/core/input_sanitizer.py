"""
Input sanitization utilities to prevent XSS and injection attacks.
"""
import html
import re
from typing import Any, Dict, List, Union


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML content by escaping special characters.
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        HTML-escaped text safe for display
    """
    if not isinstance(text, str):
        return str(text)
    
    return html.escape(text, quote=True)


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent directory traversal and invalid characters.
    
    Args:
        filename: Input filename
        max_length: Maximum allowed filename length
        
    Returns:
        Safe filename
    """
    if not isinstance(filename, str):
        raise ValueError("Filename must be a string")
    
    # Remove path separators and null bytes
    filename = filename.replace('/', '_').replace('\\', '_').replace('\0', '')
    
    # Remove or replace other dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Trim to max length
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = max_length - len(ext) - 1
        filename = f"{name[:max_name_length]}.{ext}" if ext else name[:max_length]
    
    return filename.strip()


def sanitize_json_input(data: Union[Dict[str, Any], List[Any], str]) -> Union[Dict[str, Any], List[Any], str]:
    """
    Recursively sanitize JSON data to prevent XSS in string values.
    
    Args:
        data: Input JSON data (dict, list, or string)
        
    Returns:
        Sanitized data with HTML-escaped strings
    """
    if isinstance(data, dict):
        return {k: sanitize_json_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json_input(item) for item in data]
    elif isinstance(data, str):
        return sanitize_html(data)
    else:
        return data


def validate_destination(destination: str) -> str:
    """
    Validate and sanitize a destination string.
    
    Args:
        destination: Destination name/location
        
    Returns:
        Validated destination string
        
    Raises:
        ValueError: If destination is invalid
    """
    if not destination or not destination.strip():
        raise ValueError("Destination cannot be empty")
    
    destination = destination.strip()
    
    # Length validation
    if len(destination) > 100:
        raise ValueError("Destination name is too long (max 100 characters)")
    
    if len(destination) < 2:
        raise ValueError("Destination name is too short (min 2 characters)")
    
    # Allow only alphanumeric, spaces, hyphens, apostrophes, and common accented characters
    if not re.match(r'^[a-zA-Z0-9\s\-\'À-ÿ]+$', destination):
        raise ValueError("Destination contains invalid characters")
    
    return destination


def sanitize_language_code(lang: str, supported_languages: List[str]) -> str:
    """
    Validate language code against supported languages.
    
    Args:
        lang: Language code (e.g., 'en', 'es')
        supported_languages: List of valid language codes
        
    Returns:
        Validated language code
        
    Raises:
        ValueError: If language code is invalid
    """
    if not lang or not isinstance(lang, str):
        return 'en'  # Default to English
    
    lang = lang.lower().strip()
    
    # Must be 2-5 characters (e.g., 'en', 'en-US')
    if not re.match(r'^[a-z]{2}(-[a-z]{2})?$', lang, re.IGNORECASE):
        return 'en'
    
    # Check if supported
    if lang not in supported_languages:
        return 'en'
    
    return lang
