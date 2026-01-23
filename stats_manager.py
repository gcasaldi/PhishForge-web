"""
PhishForge Statistics Manager - Enterprise Metrics

Real-time anonymous statistics tracking for SOC/SIEM integration.
No PII stored - only aggregated counters.

Author: PhishForge Team
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict
import logging
from threading import Lock

logger = logging.getLogger(__name__)

# Thread-safe lock for concurrent writes
_stats_lock = Lock()

# Stats file location
STATS_FILE = Path(__file__).parent / "stats.json"


def load_stats() -> Dict:
    """
    Load statistics from persistent storage.
    
    Returns:
        dict: Statistics dictionary with structure:
            {
                "since": "2025-11-28",
                "total_analyzed": 0,
                "high_risk": 0,
                "critical_risk": 0
            }
    """
    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
            logger.debug(f"Stats loaded: {stats}")
            return stats
        else:
            # Initialize with defaults
            default_stats = {
                "since": datetime.now().strftime("%Y-%m-%d"),
                "total_analyzed": 0,
                "high_risk": 0,
                "critical_risk": 0
            }
            save_stats(default_stats)
            logger.info(f"Initialized new stats file: {STATS_FILE}")
            return default_stats
    except Exception as e:
        logger.error(f"Error loading stats: {e}")
        # Return safe defaults
        return {
            "since": datetime.now().strftime("%Y-%m-%d"),
            "total_analyzed": 0,
            "high_risk": 0,
            "critical_risk": 0
        }


def save_stats(stats: Dict) -> None:
    """
    Save statistics to persistent storage (thread-safe).
    
    Args:
        stats: Statistics dictionary to save
    """
    try:
        with _stats_lock:
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f, indent=2)
            logger.debug(f"Stats saved: {stats}")
    except Exception as e:
        logger.error(f"Error saving stats: {e}")


def update_stats(final_score: float, risk_level: str | None = None) -> None:
    """
    Update statistics based on analysis result (real-time, thread-safe).
    
    Tracks all 4 mutually exclusive categories: LOW, MEDIUM, HIGH, CRITICAL
    
    Increments:
    - total_analyzed: always +1
    - low_risk: if risk_level is LOW
    - medium_risk: if risk_level is MEDIUM
    - high_risk: if risk_level is HIGH or CRITICAL (legacy compatibility)
    - critical_risk: if risk_level is CRITICAL
    
    Args:
        final_score: Risk score from analysis (0-100)
        risk_level: Mutually exclusive classification (LOW/MEDIUM/HIGH/CRITICAL)
                   If provided, this takes precedence over score thresholds
    """
    try:
        stats = load_stats()
        
        # Always increment total
        stats["total_analyzed"] += 1
        
        # Use risk_level if provided (preferred), otherwise fallback to score
        if risk_level:
            risk_level_upper = str(risk_level).upper()
            
            # Track each category separately
            if risk_level_upper == "LOW":
                stats["low_risk"] = stats.get("low_risk", 0) + 1
            elif risk_level_upper == "MEDIUM":
                stats["medium_risk"] = stats.get("medium_risk", 0) + 1
            elif risk_level_upper == "HIGH":
                stats["high_risk"] = stats.get("high_risk", 0) + 1
            elif risk_level_upper == "CRITICAL":
                stats["high_risk"] = stats.get("high_risk", 0) + 1  # Legacy compatibility
                stats["critical_risk"] = stats.get("critical_risk", 0) + 1
                
            logger.info(f"Stats updated by risk_level={risk_level_upper} - Total: {stats['total_analyzed']}, "
                       f"Low: {stats.get('low_risk', 0)}, Medium: {stats.get('medium_risk', 0)}, "
                       f"High: {stats.get('high_risk', 0)}, Critical: {stats.get('critical_risk', 0)}")
        else:
            # Fallback to score thresholds (legacy)
            if final_score < 40:
                stats["low_risk"] = stats.get("low_risk", 0) + 1
            elif final_score < 70:
                stats["medium_risk"] = stats.get("medium_risk", 0) + 1
            elif final_score < 90:
                stats["high_risk"] = stats.get("high_risk", 0) + 1
            else:  # >= 90
                stats["high_risk"] = stats.get("high_risk", 0) + 1
                stats["critical_risk"] = stats.get("critical_risk", 0) + 1
            
            logger.info(f"Stats updated by score={final_score} - Total: {stats['total_analyzed']}, "
                       f"Low: {stats.get('low_risk', 0)}, Medium: {stats.get('medium_risk', 0)}, "
                       f"High: {stats.get('high_risk', 0)}, Critical: {stats.get('critical_risk', 0)}")
        
        save_stats(stats)
        
    except Exception as e:
        logger.error(f"Error updating stats: {e}")
        # Non-fatal - continue processing


def reset_stats() -> None:
    """
    Reset statistics (admin function).
    
    WARNING: This will reset all counters to zero.
    """
    default_stats = {
        "since": datetime.now().strftime("%Y-%m-%d"),
        "total_analyzed": 0,
        "high_risk": 0,
        "critical_risk": 0
    }
    save_stats(default_stats)
    logger.warning("Statistics have been reset")


def get_stats_summary() -> str:
    """
    Get human-readable stats summary.
    
    Returns:
        str: Formatted statistics summary
    """
    stats = load_stats()
    
    total = stats.get("total_analyzed", 0)
    high = stats.get("high_risk", 0)
    critical = stats.get("critical_risk", 0)
    
    high_pct = (high / total * 100) if total > 0 else 0
    critical_pct = (critical / total * 100) if total > 0 else 0
    
    summary = f"""
PhishForge Statistics (since {stats.get('since', 'N/A')})
{'='*50}
Total Analyzed:    {total:,}
High Risk (70+):   {high:,} ({high_pct:.1f}%)
Critical (90+):    {critical:,} ({critical_pct:.1f}%)
"""
    return summary
