"""
Email Predictor Stub - Fallback Module

This module provides fallback functions when the email ML model is not available.
The system continues to work with heuristic detection only.
"""

import logging

logger = logging.getLogger(__name__)

def predict_email_risk(subject: str, body: str) -> float:
    """
    Fallback function that returns 0 when ML model is not available.
    System continues with heuristic detection.
    
    Args:
        subject: Email subject
        body: Email body
        
    Returns:
        0.0 (ML model not available)
    """
    return 0.0

def is_model_available() -> bool:
    """
    Check if email ML model is available.
    
    Returns:
        False (fallback mode)
    """
    return False
