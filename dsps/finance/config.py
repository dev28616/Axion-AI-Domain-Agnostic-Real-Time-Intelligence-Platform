class FinanceDSPConfig:
    DATA_FILE = "dsps/finance/data/transactions.csv"
    MODEL_PATH = "dsps/finance/models/fraud_model.joblib"
    TOPIC_RAW_EVENTS = "finance-raw-events"
    TOPIC_ANALYTICS_RESULTS = "finance-analytics-results"
    TOPIC_DECISIONS = "finance-decisions"
    GROUP_ENRICHMENT = "finance-enrichment-agent"
    GROUP_DECISION = "finance-decision-agent"
    GROUP_UI = "finance-ui-agent"
    DECISION_THRESHOLD = 0.90

