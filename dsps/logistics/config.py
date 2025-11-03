class LogisticsDSPConfig:
    DATA_FILE = "dsps/logistics/data/shipments.csv"
    MODEL_PATH = "dsps/logistics/models/anomaly_model.joblib"
    TOPIC_RAW_EVENTS = "logistics-raw-events"
    TOPIC_ANALYTICS_RESULTS = "logistics-analytics-results"
    TOPIC_DECISIONS = "logistics-decisions"
    GROUP_ENRICHMENT = "logistics-enrichment-agent"
    GROUP_DECISION = "logistics-decision-agent"
    GROUP_UI = "logistics-ui-agent"
    DECISION_THRESHOLD = 0.65

