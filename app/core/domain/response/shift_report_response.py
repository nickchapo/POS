from pydantic import BaseModel


class ShiftReportResponse(BaseModel):
    shift_id: str
    receipts_count: int
    items_sold: dict[str, int]
    revenue: dict[str, float]
