from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import uuid

class IncomeCreate(BaseModel):
    date: str
    type: str
    amount: float
    description: str

    @validator('date')
    def validate_date(cls, v):
        # 如果日期包含时间部分，只保留日期
        if 'T' in v:
            v = v.split('T')[0]
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

class Income(BaseModel):
    id: str = str(uuid.uuid4())
    date: str
    type: str
    amount: float
    description: str

class IncomeGoal(BaseModel):
    id: str = str(uuid.uuid4())
    period: str  # 'monthly' 或 'yearly'
    amount: float
    start_date: str
    end_date: str
    description: Optional[str] = None

    @validator('period')
    def validate_period(cls, v):
        if v not in ['monthly', 'yearly']:
            raise ValueError("Period must be either 'monthly' or 'yearly'")
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        # 如果日期包含时间部分，只保留日期
        if 'T' in v:
            v = v.split('T')[0]
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD") 