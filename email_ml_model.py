"""
Email ML Model Inference Module

Provides risk scoring for emails using trained TF-IDF + LogisticRegression model.

ENHANCED: Now extracts URLs from emails and checks against 533k+ phishing domains
for maximum accuracy. Database hits significantly boost ML score.

Functions:
    predict_email_risk(subject: str, body: str) -> float
        Returns phishing risk score 0-100 for given email
"""

import logging
from pathlib import Path
import joblib
import numpy as np
import re
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

# Import multi-database client
try:
    from PhishForge.multi_database_client import get_client as get_multi_db_client
    MULTI_DB_AVAILABLE = True
except ImportError:
    MULTI_DB_AVAILABLE = False
    logger.warning("Multi-database not available - Email ML will work without database integration")

# Model paths
MODEL_DIR = Path(__file__).resolve().parent / "ml" / "models"
VECTORIZER_FILE = MODEL_DIR / "email_vectorizer.joblib"
MODEL_FILE = MODEL_DIR / "email_model.joblib"

# Global model instances
_vectorizer = None
_model = None


def _load_models():
    """
    Load trained vectorizer and model from disk.
    
    Returns:
        tuple: (vectorizer, model) or (None, None) if loading fails
    """
    global _vectorizer, _model
    
    if _vectorizer is not None and _model is not None:
        return _vectorizer, _model
    
    try:
        if not VECTORIZER_FILE.exists():
            logger.warning(f"Email vectorizer not found: {VECTORIZER_FILE}")
            logger.warning("Train model with: python ml/train_email_model.py")
            return None, None
        
        if not MODEL_FILE.exists():
            logger.warning(f"Email model not found: {MODEL_FILE}")
            logger.warning("Train model with: python ml/train_email_model.py")
            return None, None
        
        logger.info(f"Loading email vectorizer from: {VECTORIZER_FILE}")
        _vectorizer = joblib.load(VECTORIZER_FILE)
        
        logger.info(f"Loading email model from: {MODEL_FILE}")
        _model = joblib.load(MODEL_FILE)
        
        logger.info("✅ Email ML models loaded successfully")
        return _vectorizer, _model
        
    except Exception as e:
        logger.error(f"Failed to load email ML models: {e}")
        return None, None


def predict_email_risk(subject: str, body: str) -> float:
    """
    Calculate ML-based phishing risk score for an email.
    
    ENHANCED: Extracts URLs and checks against 533k+ phishing domains.
    If phishing URL found, score is boosted to 90+.
    
    Uses a trained TF-IDF + Logistic Regression model to predict
    the probability that an email is phishing based on its content.
    
    Args:
        subject (str): Email subject line
        body (str): Email body content
        
    Returns:
        float: Phishing probability score between 0-100
               Returns 50 if models unavailable or error occurs
    
    Examples:
        >>> predict_email_risk("Verify your account", "Click here to verify...")
        87.3
        >>> predict_email_risk("Meeting tomorrow", "See you at 2pm")
        4.2
        >>> predict_email_risk("Urgent", "https://paypal-verify.ru/login")
        95.0  # URL found in database
    """
    if not subject and not body:
        return 50.0
    
    # Ensure inputs are strings
    subject = str(subject) if subject else ""
    body = str(body) if body else ""
    
    try:
        # STEP 1: Extract and check URLs against database (PRIORITY)
        database_hit = False
        if MULTI_DB_AVAILABLE:
            try:
                # Extract URLs from email
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                text = f"{subject} {body}"
                urls = re.findall(url_pattern, text, re.IGNORECASE)
                
                if urls:
                    multi_db = get_multi_db_client()
                    for url in urls[:10]:  # Check max 10 URLs
                        try:
                            parsed = urlparse(url)
                            domain = parsed.netloc or parsed.path.split('/')[0]
                            
                            if multi_db.is_phishing(domain):
                                logger.info(f"🚨 Email ML: Phishing URL detected in database: {domain}")
                                database_hit = True
                                break  # One hit is enough
                        except:
                            continue
            except Exception as e:
                logger.debug(f"URL extraction/check failed: {e}")
        
        # If database hit, return very high score immediately
        if database_hit:
            return 95.0  # Almost certain phishing
        
        # STEP 2: Use ML model for content analysis
        # Load models if not already loaded
        vectorizer, model = _load_models()
        if vectorizer is None or model is None:
            return 50.0  # Neutral when no model available
        
        # Combine subject and body
        text = f"{subject} {body}"
        
        # Transform to TF-IDF features
        features = vectorizer.transform([text])
        
        # Get prediction probability
        # predict_proba returns [[prob_legit, prob_phishing]]
        prob_phishing = model.predict_proba(features)[0][1]
        
        # Convert to 0-100 scale
        score = prob_phishing * 100
        
        # Clamp to valid range
        score = max(0.0, min(100.0, score))
        
        logger.debug(f"Email ML score: {score:.1f}")
        return score
        
    except Exception as e:
        logger.error(f"Error computing email ML score: {e}")
        return 50.0  # Neutral on error


def is_email_model_available() -> bool:
    """
    Check if email ML models are available and loaded.
    
    Returns:
        bool: True if models are ready, False otherwise
    """
    vectorizer, model = _load_models()
    return vectorizer is not None and model is not None


# Preload models on import
_load_models()
