"""
Hallucination Detection & Validation (Giga JD Requirement)
Prevents hallucinations with confidence scoring and validation
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Known patterns that indicate hallucinations
HALLUCINATION_PATTERNS = {
    "absolute_claims": [r"\balways\b", r"\bnever\b", r"\bimpossible\b"],
    "invented_facts": [r"\bI invented\b", r"\bI created\b", r"\bI developed\b"],
    "future_claims": [r"\bwill definitely\b", r"\bwill certainly\b"],
    "unqualified_statements": [r"\bproven\b", r"\bundeniable\b"]
}

def validate_response(response: str) -> Dict[str, Any]:
    """
    Validate response for hallucinations
    Returns: {"status": "passed|flagged|failed", "issues": [...], "score": 0.0-1.0}
    """
    
    if not isinstance(response, str):
        response = str(response)
    
    issues = []
    confidence = 1.0
    
    # Check for hallucination patterns
    for pattern_type, patterns in HALLUCINATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issue = f"Found absolute claim pattern: {pattern_type}"
                issues.append(issue)
                confidence -= 0.15
    
    # Check for contradictions (sentences with "but" or "however")
    contradiction_matches = re.findall(r"[^.!?]*\b(but|however)\b[^.!?]*", response)
    if contradiction_matches:
        for match in contradiction_matches[:2]:  # Limit to 2
            issues.append("Potential contradiction detected")
            confidence -= 0.10
    
    # Check response length (too short = incomplete)
    if len(response.split()) < 20:
        issues.append("Response too short (may be incomplete)")
        confidence -= 0.20
    
    # Check for quoted statements (source attribution)
    quote_count = len(re.findall(r'["\'`]', response))
    if quote_count == 0 and len(response) > 200:
        issues.append("No quoted sources found")
        confidence -= 0.05
    
    # Determine validation status
    if len(issues) > 3:
        status = "failed"
    elif len(issues) > 0:
        status = "flagged"
    else:
        status = "passed"
    
    return {
        "status": status,
        "issues": issues,
        "confidence": max(0.0, confidence),
        "issue_count": len(issues)
    }

def calculate_confidence(response: str, validation: Dict[str, Any]) -> float:
    """
    Calculate final confidence score (0.0-1.0)
    Combines multiple factors
    """
    
    validation_confidence = validation.get("confidence", 1.0)
    
    # Response quality factors
    response_len = len(str(response).split())
    length_score = min(response_len / 200, 1.0)  # 200 words = max score
    
    # Source citation score
    citation_score = 0.8 if '"' in response or "'" in response else 0.6
    
    # Combine scores (weighted)
    confidence = (
        validation_confidence * 0.5 +
        length_score * 0.2 +
        citation_score * 0.3
    )
    
    logger.debug(f"Confidence calculation: val={validation_confidence:.2f}, len={length_score:.2f}, cite={citation_score:.2f} → final={confidence:.2f}")
    
    return round(confidence, 2)

def get_confidence_level(confidence: float) -> str:
    """Get human-readable confidence level"""
    if confidence >= 0.85:
        return "Very High"
    elif confidence >= 0.70:
        return "High"
    elif confidence >= 0.50:
        return "Medium"
    else:
        return "Low"
