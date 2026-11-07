from app.models import LeadUrgency


def analyze_lead(message: str, service_type: str) -> dict:
    text = message.lower()
    service = service_type.lower()

    # Identify customer intent
    if any(word in text for word in ["install", "installation", "new system"]):
        intent = "installation_request"
    elif any(word in text for word in ["repair", "broken", "not working", "stopped"]):
        intent = "repair_request"
    elif any(word in text for word in ["quote", "price", "cost", "estimate"]):
        intent = "pricing_request"
    elif any(word in text for word in ["maintain", "maintenance", "service check"]):
        intent = "maintenance_request"
    else:
        intent = "general_enquiry"

    # Detect urgency signals
    urgent_words = [
        "emergency", "urgent", "immediately", "right now",
        "flooding", "leaking", "no heat", "no cooling",
        "sparking", "smoke", "gas smell", "stopped working"
    ]

    high_urgency = any(word in text for word in urgent_words)

    medium_words = [
        "today", "tomorrow", "soon", "asap",
        "this week", "not working properly"
    ]

    medium_urgency = any(word in text for word in medium_words)

    if high_urgency:
        urgency = LeadUrgency.HIGH
    elif medium_urgency:
        urgency = LeadUrgency.MEDIUM
    else:
        urgency = LeadUrgency.LOW

    # Recommend the next business action
    if urgency == LeadUrgency.HIGH:
        action = "Prioritize a human callback"
    elif intent == "pricing_request":
        action = "Prepare a quote and contact the customer"
    elif intent == "installation_request":
        action = "Arrange an installation consultation"
    elif intent == "maintenance_request":
        action = "Schedule a maintenance discussion"
    else:
        action = "Contact the customer to understand their needs"

    # Human review is required for urgent or safety-sensitive cases
    safety_words = [
        "gas smell", "smoke", "sparking",
        "electrical fire", "flooding"
    ]

    requires_review = (
        urgency == LeadUrgency.HIGH
        or any(word in text for word in safety_words)
    )

    return {
        "urgency": urgency,
        "customer_intent": intent,
        "recommended_action": action,
        "requires_human_review": requires_review,
    }