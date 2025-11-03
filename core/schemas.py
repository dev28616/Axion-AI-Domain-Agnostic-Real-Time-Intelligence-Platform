from pydantic import BaseModel

class RawEvent(BaseModel):
    event_id: str
    source_id: str
    event_value: str
    source_name: str
    description: str
    timestamp: str

class CleanedEvent(BaseModel):
    event_id: str
    source_id: str
    event_value: float
    source_name: str
    description: str
    timestamp: str

class AnalyticsResult(BaseModel):
    event: CleanedEvent
    score: float
    vector_embedding: list[float]

class FinalDecision(BaseModel):
    event_id: str
    decision: str
    reason: str

