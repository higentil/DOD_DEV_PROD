import json

def analyze_battlefield_report(raw_text: str) -> str:
    """Applies strict keyword classification matrices to generate low-bandwidth JSON metrics."""
    text_lower = raw_text.lower()
    
    red_keywords = {"fire", "engagement", "pinned", "shooting", "ambush", "sniper", "attack", "hostile", "contact"}
    amber_keywords = {"stuck", "broken", "overheat", "mud", "flood", "mechanical", "stationary", "engine", "tow", "failure"}
    med_keywords = {"wound", "injured", "casualty", "bleeding", "hurt", "medevac", "doctor", "shrapnel", "medic", "blood"}
    
    medical_urgency = any(kw in text_lower for kw in med_keywords)
    
    threat_level = "GREEN"
    if any(kw in text_lower for kw in red_keywords):
        threat_level = "RED"
    elif any(kw in text_lower for kw in amber_keywords):
        threat_level = "AMBER"

    filler_words = {
        "the", "a", "an", "is", "are", "we", "have", "to", "our", "from", "in", "on", "at", 
        "sir", "command", "base", "this", "that", "there", "with", "but", "and", "for", "of"
    }
    
    raw_words = [word.strip(".,!?\"'();:") for word in raw_text.split()]
    critical_tokens = [w for w in raw_words if w.lower() not in filler_words]
    
    if critical_tokens:
        summary = f"[{threat_level}] " + " ".join(critical_tokens[:7]) + "..."
    else:
        summary = f"[{threat_level}] Operational tracking clear."

    return json.dumps({
        "threat_level": threat_level,
        "summary": summary,
        "medical_urgency": medical_urgency
    })
