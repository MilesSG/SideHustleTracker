from fastapi import APIRouter, HTTPException
from models.income import Income, IncomeCreate, IncomeGoal
import json
import os
from typing import List
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 获取数据文件路径
def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def get_income_file():
    return os.path.join(get_data_dir(), "incomes.json")

def get_goals_file():
    return os.path.join(get_data_dir(), "goals.json")

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

# 读取所有目标数据
def read_goals():
    file_path = get_goals_file()
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [IncomeGoal(**item) for item in data]
    except Exception as e:
        logger.error(f"Error reading goals file: {str(e)}")
        return []

# 保存目标数据
def save_goals(goals: List[IncomeGoal]):
    file_path = get_goals_file()
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([goal.model_dump() for goal in goals], f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving goals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save goals: {str(e)}")

# 收入相关路由
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

# 目标相关路由
@router.get("/goals", response_model=List[IncomeGoal])
async def get_all_goals():
    try:
        return read_goals()
    except Exception as e:
        logger.error(f"Error getting goals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get goals: {str(e)}")

@router.post("/goals", response_model=IncomeGoal)
async def create_goal(goal: IncomeGoal):
    try:
        logger.info(f"Creating new goal: {goal.model_dump()}")
        goals = read_goals()
        goals.append(goal)
        save_goals(goals)
        return goal
    except Exception as e:
        logger.error(f"Error creating goal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create goal: {str(e)}")

@router.put("/goals/{goal_id}", response_model=IncomeGoal)
async def update_goal(goal_id: str, goal_update: IncomeGoal):
    try:
        logger.info(f"Updating goal {goal_id}: {goal_update.model_dump()}")
        goals = read_goals()
        for i, goal in enumerate(goals):
            if goal.id == goal_id:
                goals[i] = goal_update
                save_goals(goals)
                return goal_update
        raise HTTPException(status_code=404, detail="Goal not found")
    except Exception as e:
        logger.error(f"Error updating goal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update goal: {str(e)}")

@router.delete("/goals/{goal_id}")
async def delete_goal(goal_id: str):
    try:
        logger.info(f"Deleting goal {goal_id}")
        goals = read_goals()
        initial_length = len(goals)
        goals = [goal for goal in goals if goal.id != goal_id]
        if len(goals) == initial_length:
            raise HTTPException(status_code=404, detail="Goal not found")
        save_goals(goals)
        return {"message": "Goal deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting goal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete goal: {str(e)}")

# 获取目标完成情况
@router.get("/goals/progress")
async def get_goals_progress():
    goals = read_goals()
    incomes = read_incomes()
    
    progress = []
    for goal in goals:
        # 处理日期字符串，移除时间部分
        start_date = goal.start_date.split('T')[0] if 'T' in goal.start_date else goal.start_date
        end_date = goal.end_date.split('T')[0] if 'T' in goal.end_date else goal.end_date
        
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 计算该时间段内的总收入
        total_income = sum(
            income.amount
            for income in incomes
            if start_date <= datetime.strptime(income.date.split('T')[0], "%Y-%m-%d") <= end_date
        )
        
        # 计算完成度
        completion_rate = (total_income / goal.amount) * 100 if goal.amount > 0 else 0
        
        progress.append({
            "goal": goal,
            "current_amount": total_income,
            "completion_rate": round(completion_rate, 2)
        })
    
    return progress 