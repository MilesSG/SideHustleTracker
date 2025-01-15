from fastapi import APIRouter, HTTPException
from models.income import Income, IncomeCreate
import json
import os
from typing import List
from datetime import datetime

router = APIRouter()

# 获取收入数据文件路径
def get_income_file():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "incomes.json")

# 读取所有收入数据
def read_incomes():
    file_path = get_income_file()
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Income(**item) for item in data]

# 保存收入数据
def save_incomes(incomes: List[Income]):
    file_path = get_income_file()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([income.model_dump() for income in incomes], f, ensure_ascii=False, indent=2, default=str)

@router.get("/incomes", response_model=List[Income])
async def get_all_incomes():
    return read_incomes()

@router.post("/incomes", response_model=Income)
async def create_income(income: IncomeCreate):
    incomes = read_incomes()
    new_income = Income(**income.model_dump())
    incomes.append(new_income)
    save_incomes(incomes)
    return new_income

@router.get("/incomes/{income_id}", response_model=Income)
async def get_income(income_id: str):
    incomes = read_incomes()
    for income in incomes:
        if income.id == income_id:
            return income
    raise HTTPException(status_code=404, detail="Income not found")

@router.put("/incomes/{income_id}", response_model=Income)
async def update_income(income_id: str, income_update: IncomeCreate):
    incomes = read_incomes()
    for i, income in enumerate(incomes):
        if income.id == income_id:
            updated_income = Income(id=income_id, **income_update.model_dump())
            incomes[i] = updated_income
            save_incomes(incomes)
            return updated_income
    raise HTTPException(status_code=404, detail="Income not found")

@router.delete("/incomes/{income_id}")
async def delete_income(income_id: str):
    incomes = read_incomes()
    initial_length = len(incomes)
    incomes = [income for income in incomes if income.id != income_id]
    if len(incomes) == initial_length:
        raise HTTPException(status_code=404, detail="Income not found")
    save_incomes(incomes)
    return {"message": "Income deleted successfully"} 