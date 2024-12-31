from pydantic import BaseModel


class SurfReportResponse(BaseModel):
    chart: str
    wave_height: int
    alerts: str
