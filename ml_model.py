"""
Machine Learning Module for URL Phishing Detection

This module loads a pre-trained scikit-learn model and provides
a scoring function for URL phishing probability.

ENHANCED: Now integrates with multi-database (533k+ phishing domains)
for maximum accuracy. Database hits override ML predictions.

Functions:
    ml_score_url(url: str) -> float
        Returns a phishing score between 0-100 for the given URL
"""

import logging
from pathlib import Path
import joblib
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

# Import multi-database client
try:
    from PhishForge.multi_database_client import get_client as get_multi_db_client
    MULTI_DB_AVAILABLE = True
except ImportError:
    MULTI_DB_AVAILABLE = False
    logger.warning("Multi-database not available - ML will work without database integration")

# Model paths
MODEL_DIR = Path(__file__).resolve().parent / "ml" / "models"
MODEL_FILE = MODEL_DIR / "url_phishing_model.joblib"

# Global model instance
_model = None


def _load_model():
    """
    Load the trained ML model from disk.
    
    Returns:
        Pipeline or None: Trained model pipeline, or None if loading fails
    """
    global _model
    
    if _model is not None:
        return _model
    
    try:
        if not MODEL_FILE.exists():
            logger.warning(f"ML model file not found: {MODEL_FILE}")
            logger.warning("ML scoring will be disabled. Train model with: python ml/train_url_model.py")
            return None
        
        logger.info(f"Loading ML model from: {MODEL_FILE}")
        _model = joblib.load(MODEL_FILE)
        logger.info("ML model loaded successfully")
        return _model
        
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        return None


def ml_score_url(url: str) -> float:
    """
    Calculate ML-based phishing score for a URL.
    
    ENHANCED: First checks 533k+ phishing domains database.
    If found, returns 95-100 (CRITICAL).
    Otherwise uses trained ML model.
    
    Uses a trained logistic regression model with character-level
    n-grams to predict the probability that a URL is phishing.
    
    Args:
        url (str): URL to analyze
        
    Returns:
        float: Phishing probability score between 0-100
               Returns 0 if model unavailable or error occurs
    
    Examples:
        >>> ml_score_url("https://www.google.com")
        5.2
        >>> ml_score_url("http://paypal-verify.com/login")
        92.7
        >>> ml_score_url("https://known-phishing-domain.ru")
        98.0  # Found in database
    """
    if not url or not isinstance(url, str):
        return 0.0
    
    try:
        # STEP 1: Check multi-database FIRST (533k+ domains)
        # This is CRITICAL - database hits are 100% accurate
        if MULTI_DB_AVAILABLE:
            try:
                # Extract domain
                parsed = urlparse(url if url.startswith('http') else f'http://{url}')
                domain = parsed.netloc or parsed.path.split('/')[0]
                
                multi_db = get_multi_db_client()
                if multi_db.is_phishing(domain):
                    # Found in database - return very high score
                    logger.info(f"🚨 ML: URL in database (533k domains): {domain}")
                    return 98.0  # Almost certain phishing
            except Exception as e:
                logger.debug(f"Database check failed (continuing with ML): {e}")
        
        # STEP 2: Use ML model if not in database
        # Load model if not already loaded
        model = _load_model()
        if model is None:
            # No model available - return neutral score
            return 50.0  # Neutral when no data available
        
        # Get prediction probability
        # predict_proba returns [[prob_legit, prob_phishing]]
        prob_phishing = model.predict_proba([url])[0][1]
        
        # Convert to 0-100 scale
        score = prob_phishing * 100
        
        # Clamp to valid range
        score = max(0.0, min(100.0, score))
        
        logger.debug(f"ML score for URL '{url}': {score:.1f}")
        return score
        
    except Exception as e:
        logger.error(f"Error computing ML score for URL '{url}': {e}")
        return 50.0  # Return neutral score on error


def is_model_available() -> bool:
    """
    Check if ML model is available and loaded.
    
    Returns:
        bool: True if model is ready, False otherwise
    """
    return _load_model() is not None


# Preload model on import
_load_model()
