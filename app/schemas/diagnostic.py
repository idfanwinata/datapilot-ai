
from pydantic import BaseModel, Field


class DiagnosticRequest(BaseModel):
    application: str = Field(
        min_length=1,
        description="Nama aplikasi yang mengalami error",
    )
    error_log: str = Field(
        min_length=1,
        description="Log error yang ingin dianalisis",
    )


class DiagnosticResponse(BaseModel):
    application: str
    error_summary: str
    possible_cause: str
    recommended_steps: list[str]
    analysis_type: str = "mock"
