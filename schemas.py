from pydantic import BaseModel
from datetime import datetime

class QueryRequest(BaseModel):
    doctor_id: str
    doctor_name: str
    area_of_expertise: str
    query: str

    class Config:
        orm_mode= True

class QueryResponse(BaseModel):
    response: str


    class Config:
        orm_mode= True


