from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class base_campaign_request(BaseModel):
    active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
