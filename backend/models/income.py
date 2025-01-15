from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class IncomeBase(BaseModel):
    date: datetime
    type: str = Field(..., pattern="^(salary|thesis|subsidy|other)$")
    amount: float = Field(..., gt=0)
    description: str

class IncomeCreate(IncomeBase):
    pass

class Income(IncomeBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    class Config:
        from_attributes = True 