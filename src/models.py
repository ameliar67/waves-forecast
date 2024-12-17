from pydantic import BaseModel

class SurfReportRequest(BaseModel):
    wave_model: str
    hours_to_forecast: int
    selected_location: str

class SurfReportResponse(BaseModel):
    plot_image: str
