class HealthcareDSPConfig:
    DATA_FILE = "dsps/healthcare/data/claims.csv"
    MODEL_PATH = "dsps/healthcare/models/claim_approval_model.joblib"
    TOPIC_RAW_EVENTS = "healthcare-raw-events"
    TOPIC_ANALYTICS_RESULTS = "healthcare-analytics-results"
    TOPIC_DECISIONS = "healthcare-decisions"
    GROUP_ENRICHMENT = "healthcare-enrichment-agent"
    GROUP_DECISION = "healthcare-decision-agent"
    GROUP_UI = "healthcare-ui-agent"
    DECISION_THRESHOLD = 0.95

