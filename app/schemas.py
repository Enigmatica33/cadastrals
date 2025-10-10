from datetime import datetime

from pydantic import BaseModel


class QueryRequest(BaseModel):
    cadastral_number: str
    latitude: float
    longitude: float


class HistoryBase(QueryRequest):
    pass


class HistoryCreate(HistoryBase):
    server_response: bool


class History(HistoryBase):
    id: int
    server_response: bool
    created_at: datetime

    class Config:
        from_attributes = True
