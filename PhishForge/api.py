from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import importlib.util
import sys
from pathlib import Path

# Import the detector module
detector_path = Path(__file__).parent / "phishforge_detector.py"
spec = importlib.util.spec_from_file_location("detector", detector_path)
detector = importlib.util.module_from_spec(spec)
sys.modules["detector"] = detector
spec.loader.exec_module(detector)

app = FastAPI(
    title="PhishForge API",
    description="API for phishing email detection with detailed risk analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gcasaldi.github.io",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5500"  # Per Live Server in sviluppo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class EmailAnalysisRequest(BaseModel):
    sender: str = Field(..., description="Indirizzo email del mittente (es: 'PayPal <noreply@paypal-secure.xyz>')")
    subject: str = Field(..., description="Oggetto dell'email")
    body: str = Field(..., description="Corpo dell'email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender": "PayPal Security <noreply@paypal-secure.xyz>",
                "subject": "Urgent: Verify your account immediately!",
                "body": "Your PayPal account has been locked. Click here to verify: http://bit.ly/verify123"
            }
        }

class Finding(BaseModel):
    risk_score: int
    category: str
    detail: str
    url: Optional[str] = None
    educational: Dict

class EmailAnalysisResponse(BaseModel):
    risk_score: int = Field(..., description="Total risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    risk_percentage: float = Field(..., description="Risk percentage (0-100)")
    findings: List[Finding] = Field(..., description="List of detected issues")
    urls: List[str] = Field(..., description="URLs found in email")
    recommendation: str = Field(..., description="Recommendation based on risk level")

class HealthResponse(BaseModel):
    status: str
    version: str
    detector_loaded: bool

# Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PhishForge API is running",
        "docs": "/docs",
        "health": "/health",
        "analyze": "/analyze (POST)"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API status"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "detector_loaded": hasattr(detector, 'score_email')
    }

@app.post("/analyze", response_model=EmailAnalysisResponse)
async def analyze_email(request: EmailAnalysisRequest):
    """
    Analyze an email to detect phishing signals
    
    - **sender**: Sender's email address
    - **subject**: Email subject
    - **body**: Email body
    
    Returns detailed analysis with risk score and recommendations
    """
    try:
        # Analyze email using the detector
        result = detector.score_email(
            subject=request.subject,
            sender=request.sender,
            body=request.body
        )
        
        # Add risk-based recommendations in English
        recommendations = {
            "high": "🚨 HIGH RISK: Do not click any links or provide personal information. Delete this email immediately.",
            "medium": "⚠️ SUSPICIOUS: Verify carefully before interacting. Contact the company directly if in doubt.",
            "low": "✅ Low risk, but stay vigilant. Always verify sender identity for unusual requests."
        }
        
        # Normalize response for API
        response = {
            "risk_score": result.get("score", 0),
            "risk_level": result.get("risk_level", "unknown"),
            "risk_percentage": float(result.get("score", 0)),
            "findings": result.get("findings", []),
            "urls": result.get("urls", []),
            "recommendation": recommendations.get(result.get("risk_level", "low"), "Analysis completed")
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")

@app.get("/keywords")
async def get_suspicious_keywords():
    """Returns the list of suspicious keywords used in the analysis"""
    return {
        "keywords": detector.SUSPICIOUS_KEYWORDS,
        "count": len(detector.SUSPICIOUS_KEYWORDS)
    }

@app.get("/tlds")
async def get_suspicious_tlds():
    """Returns the list of suspicious TLDs used in the analysis"""
    return {
        "tlds": detector.SUSPICIOUS_TLDS,
        "count": len(detector.SUSPICIOUS_TLDS)
    }

@app.get("/url-shorteners")
async def get_url_shorteners():
    """Returns the list of detected URL shorteners"""
    return {
        "shorteners": detector.URL_SHORTENERS,
        "count": len(detector.URL_SHORTENERS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
