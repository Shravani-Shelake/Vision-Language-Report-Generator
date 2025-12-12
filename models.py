from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Models
class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str
    file_type: str
    message: str

class GenerateReportRequest(BaseModel):
    csv_file_ids: List[str]
    image_file_ids: List[str]
    description: Optional[str] = "Generate a comprehensive business analytics report"

# Response Models
class KeyMetric(BaseModel):
    name: str
    value: Any
    unit: Optional[str] = None

class Trend(BaseModel):
    description: str
    direction: str  # "up", "down", "stable"
    impact: str  # "positive", "negative", "neutral"

class Recommendation(BaseModel):
    priority: str  # "high", "medium", "low"
    action: str
    rationale: str

class ReportData(BaseModel):
    summary: str
    key_metrics: List[KeyMetric]
    trends: List[Trend]
    correlations: List[str]
    recommendations: List[Recommendation]
    visual_insights: List[str]
    generated_at: str

class ReportResponse(BaseModel):
    report_id: str
    status: str
    data: Optional[ReportData] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class GenerateReportResponse(BaseModel):
    report_id: str
    message: str
    status: str