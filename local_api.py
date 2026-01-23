"""
PhishForge Local API - Ottimizzata per prestazioni e sicurezza
API FastAPI locale ad alte prestazioni per rilevamento phishing.
NON ESPOSTA PUBBLICAMENTE - solo per uso locale.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
from pathlib import Path
import sys

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Aggiungi PhishForge al path
phishforge_path = Path(__file__).parent / "PhishForge"
if str(phishforge_path) not in sys.path:
    sys.path.insert(0, str(phishforge_path))

# Import detector
try:
    from phishforge_detector import analyze_email_content, analyze_url
    DETECTOR_AVAILABLE = True
    logger.info("✓ PhishForge detector caricato")
except ImportError as e:
    DETECTOR_AVAILABLE = False
    logger.error(f"✗ Errore caricamento detector: {e}")

# Import ML model
try:
    from ml_model import ml_score_url, is_model_available as ml_available
    ML_AVAILABLE = ml_available()
    logger.info(f"✓ ML model disponibile: {ML_AVAILABLE}")
except ImportError:
    ML_AVAILABLE = False
    def ml_score_url(url: str) -> float:
        return 0.0
    logger.warning("✗ ML model non disponibile")

# Import email ML
try:
    from email_ml_model import EmailMLPredictor
    email_predictor = EmailMLPredictor()
    EMAIL_ML_AVAILABLE = email_predictor.is_model_available()
    logger.info(f"✓ Email ML disponibile: {EMAIL_ML_AVAILABLE}")
except ImportError:
    EMAIL_ML_AVAILABLE = False
    logger.warning("✗ Email ML non disponibile")

# Import attachment analyzer
try:
    from attachment_analyzer import analyze_attachment
    ATTACHMENT_ANALYZER_AVAILABLE = True
    logger.info("✓ Attachment analyzer caricato")
except ImportError:
    ATTACHMENT_ANALYZER_AVAILABLE = False
    def analyze_attachment(filename: str, mime_type: Optional[str] = None, size: Optional[int] = None) -> Dict:
        return {"attachment_score": 0, "attachment_details": {}, "findings": []}
    logger.warning("✗ Attachment analyzer non disponibile")

# Inizializza FastAPI
app = FastAPI(
    title="PhishForge Local API",
    description="API locale ad alte prestazioni per rilevamento phishing",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS configuration - SOLO localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:*",
        "http://127.0.0.1",
        "http://127.0.0.1:*",
        "http://0.0.0.0:*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Modelli Pydantic
class EmailRequest(BaseModel):
    """Richiesta analisi email"""
    subject: str = Field(..., description="Oggetto dell'email")
    body: str = Field(..., description="Corpo dell'email")
    sender: Optional[str] = Field(None, description="Indirizzo mittente")
    attachments: Optional[List[Dict]] = Field(None, description="Lista allegati")

class URLRequest(BaseModel):
    """Richiesta analisi URL"""
    url: str = Field(..., description="URL da analizzare")

class AnalysisResponse(BaseModel):
    """Risposta analisi"""
    risk_score: int = Field(..., description="Punteggio di rischio (0-100)")
    risk_level: str = Field(..., description="Livello di rischio")
    risk_percentage: float = Field(..., description="Percentuale di rischio")
    findings: List[Dict] = Field(..., description="Risultati dettagliati")
    recommendation: str = Field(..., description="Raccomandazione")
    urls: Optional[List[Dict]] = Field(None, description="URL trovati")
    attachment_score: Optional[int] = Field(None, description="Score allegati")
    ml_score: Optional[float] = Field(None, description="Score ML")

# Helper functions
def calculate_risk_level(score: int) -> str:
    """Calcola il livello di rischio"""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    else:
        return "SAFE"

def generate_recommendation(risk_level: str, findings: List[Dict]) -> str:
    """Genera raccomandazione basata sul rischio"""
    if risk_level == "CRITICAL":
        return "🚨 PHISHING CONFERMATO - Elimina immediatamente questa email e NON cliccare su nessun link!"
    elif risk_level == "HIGH":
        return "⚠️ ALTA PROBABILITÀ DI PHISHING - Verifica attentamente il mittente e NON fornire dati personali!"
    elif risk_level == "MEDIUM":
        return "⚡ SOSPETTO - Procedi con cautela e verifica l'autenticità attraverso canali ufficiali."
    elif risk_level == "LOW":
        return "✓ Rischio basso ma verifica sempre i link prima di cliccare."
    else:
        return "✅ Email probabilmente sicura, ma mantieni sempre la vigilanza."

# Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "PhishForge Local API",
        "version": "2.0.0",
        "detector": DETECTOR_AVAILABLE,
        "ml_model": ML_AVAILABLE,
        "email_ml": EMAIL_ML_AVAILABLE,
        "attachment_analyzer": ATTACHMENT_ANALYZER_AVAILABLE
    }

@app.get("/health")
async def health():
    """Endpoint di salute dettagliato"""
    return {
        "status": "healthy",
        "components": {
            "detector": DETECTOR_AVAILABLE,
            "ml_model": ML_AVAILABLE,
            "email_ml": EMAIL_ML_AVAILABLE,
            "attachment_analyzer": ATTACHMENT_ANALYZER_AVAILABLE
        }
    }

@app.post("/analyze/email", response_model=AnalysisResponse)
async def analyze_email(request: EmailRequest):
    """
    Analizza un'email per rilevare tentativi di phishing.
    
    Utilizza:
    - Analisi euristica avanzata
    - Machine Learning (se disponibile)
    - Database phishing (533k+ domini)
    - Analisi allegati
    """
    if not DETECTOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Detector non disponibile")
    
    try:
        # Analisi principale con detector
        result = analyze_email_content(
            subject=request.subject,
            body=request.body,
            sender=request.sender
        )
        
        # Aggiungi analisi ML email se disponibile
        if EMAIL_ML_AVAILABLE:
            try:
                ml_risk = email_predictor.predict(request.subject, request.body)
                # Integra ML score con risultato esistente
                if ml_risk > 0.7:  # Alta probabilità phishing
                    result['risk_score'] = min(100, result.get('risk_score', 0) + 20)
                    result.setdefault('findings', []).append({
                        "risk_score": int(ml_risk * 100),
                        "category": "ml_detection",
                        "detail": f"ML model ha identificato pattern di phishing (confidenza: {ml_risk:.1%})"
                    })
            except Exception as e:
                logger.error(f"Errore ML email: {e}")
        
        # Analisi allegati
        attachment_total_score = 0
        if request.attachments and ATTACHMENT_ANALYZER_AVAILABLE:
            for attachment in request.attachments:
                att_result = analyze_attachment(
                    filename=attachment.get('filename', ''),
                    mime_type=attachment.get('mime_type'),
                    size=attachment.get('size')
                )
                attachment_total_score += att_result.get('attachment_score', 0)
                if att_result.get('findings'):
                    result.setdefault('findings', []).extend(att_result['findings'])
        
        # Calcola score finale
        base_score = result.get('risk_score', 0)
        final_score = min(100, base_score + attachment_total_score)
        
        # Genera risposta
        risk_level = calculate_risk_level(final_score)
        recommendation = generate_recommendation(risk_level, result.get('findings', []))
        
        return AnalysisResponse(
            risk_score=final_score,
            risk_level=risk_level,
            risk_percentage=final_score,
            findings=result.get('findings', []),
            recommendation=recommendation,
            urls=result.get('urls'),
            attachment_score=attachment_total_score if request.attachments else None,
            ml_score=result.get('ml_score')
        )
        
    except Exception as e:
        logger.error(f"Errore analisi email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore durante l'analisi: {str(e)}")

@app.post("/analyze/url", response_model=AnalysisResponse)
async def analyze_url_endpoint(request: URLRequest):
    """
    Analizza un URL per rilevare phishing.
    
    Utilizza:
    - Analisi euristica URL
    - Machine Learning
    - Database phishing (533k+ domini)
    """
    if not DETECTOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Detector non disponibile")
    
    try:
        # Analisi URL con detector
        result = analyze_url(request.url)
        
        # Aggiungi ML score se disponibile
        ml_score = 0.0
        if ML_AVAILABLE:
            ml_score = ml_score_url(request.url)
            if ml_score > 70:
                result['risk_score'] = min(100, result.get('risk_score', 0) + int(ml_score / 5))
                result.setdefault('findings', []).append({
                    "risk_score": int(ml_score),
                    "category": "ml_detection",
                    "detail": f"ML model ha identificato l'URL come sospetto (score: {ml_score:.1f}/100)"
                })
        
        final_score = result.get('risk_score', 0)
        risk_level = calculate_risk_level(final_score)
        recommendation = generate_recommendation(risk_level, result.get('findings', []))
        
        return AnalysisResponse(
            risk_score=final_score,
            risk_level=risk_level,
            risk_percentage=final_score,
            findings=result.get('findings', []),
            recommendation=recommendation,
            urls=[{"url": request.url, "risk_score": final_score}],
            attachment_score=None,
            ml_score=ml_score if ML_AVAILABLE else None
        )
        
    except Exception as e:
        logger.error(f"Errore analisi URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore durante l'analisi: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Ritorna statistiche del sistema"""
    return {
        "total_analyzed": 0,  # TODO: implementare contatore
        "models_active": {
            "detector": DETECTOR_AVAILABLE,
            "ml_url": ML_AVAILABLE,
            "ml_email": EMAIL_ML_AVAILABLE,
            "attachment": ATTACHMENT_ANALYZER_AVAILABLE
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Configurazione server locale
    # IMPORTANTE: host solo su localhost per sicurezza
    uvicorn.run(
        app,
        host="127.0.0.1",  # SOLO localhost
        port=8000,
        log_level="info",
        access_log=True
    )
