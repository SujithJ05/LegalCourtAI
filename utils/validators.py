"""Input validation utilities."""
from typing import Tuple


def validate_case_facts(case_facts: str, min_length: int = 50, max_length: int = 10000) -> Tuple[bool, str]:
    """
    Validate case facts input.
    
    Args:
        case_facts: The case facts text to validate
        min_length: Minimum required length
        max_length: Maximum allowed length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not case_facts:
        return False, "Case facts cannot be empty."
    
    if not isinstance(case_facts, str):
        return False, "Case facts must be a string."
    
    case_facts = case_facts.strip()
    
    if len(case_facts) < min_length:
        return False, f"Case facts must be at least {min_length} characters long."
    
    if len(case_facts) > max_length:
        return False, f"Case facts must not exceed {max_length} characters."
    
    # Check for minimum meaningful content
    words = case_facts.split()
    if len(words) < 10:
        return False, "Case facts must contain at least 10 words for meaningful analysis."
    
    return True, ""


def sanitize_input(text: str, max_length: int = None) -> str:
    """
    Sanitize user input by stripping whitespace and optionally truncating.
    
    Args:
        text: Text to sanitize
        max_length: Optional maximum length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    text = text.strip()
    
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text
