from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import logging
import json
import os
from datetime import datetime
from typing import List
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 自定义中间件，直接设置响应头
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# 处理 OPTIONS 请求
@app.options("/{rest_of_path:path}")
async def options_route(rest_of_path: str):
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INCOME_FILE = os.path.join(DATA_DIR, "incomes.json")
GOALS_FILE = os.path.join(DATA_DIR, "goals.json")

# 确保数据目录和文件存在
os.makedirs(DATA_DIR, exist_ok=True)
for file_path in [INCOME_FILE, GOALS_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)

# 辅助函数
def read_json_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return []

def write_json_file(file_path: str, data: list):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 目标相关路由
@app.get("/api/goals")
async def get_goals():
    return read_json_file(GOALS_FILE)

@app.post("/api/goals")
async def create_goal(goal: dict):
    try:
        logger.info(f"Received goal data: {goal}")
        # 添加 ID
        if "id" not in goal:
            goal["id"] = str(uuid.uuid4())
        goals = read_json_file(GOALS_FILE)
        goals.append(goal)
        write_json_file(GOALS_FILE, goals)
        return goal
    except Exception as e:
        logger.error(f"Error creating goal: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.put("/api/goals/{goal_id}")
async def update_goal(goal_id: str, goal: dict):
    try:
        logger.info(f"Updating goal {goal_id} with data: {goal}")
        goals = read_json_file(GOALS_FILE)
        for i, existing_goal in enumerate(goals):
            if existing_goal.get("id") == goal_id:
                goal["id"] = goal_id  # 确保保留原始ID
                goals[i] = goal
                write_json_file(GOALS_FILE, goals)
                return goal
        raise HTTPException(status_code=404, detail="Goal not found")
    except Exception as e:
        logger.error(f"Error updating goal: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.delete("/api/goals/{goal_id}")
async def delete_goal(goal_id: str):
    try:
        logger.info(f"Deleting goal {goal_id}")
        goals = read_json_file(GOALS_FILE)
        goals = [g for g in goals if g.get("id") != goal_id]
        write_json_file(GOALS_FILE, goals)
        return {"message": "Goal deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting goal: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/api/goals/progress")
async def get_goals_progress():
    goals = read_json_file(GOALS_FILE)
    incomes = read_json_file(INCOME_FILE)
    
    progress = []
    for goal in goals:
        try:
            # 处理日期
            start_date = goal["start_date"].split("T")[0] if "T" in goal["start_date"] else goal["start_date"]
            end_date = goal["end_date"].split("T")[0] if "T" in goal["end_date"] else goal["end_date"]
            
            # 计算总收入
            total_income = sum(
                income["amount"]
                for income in incomes
                if start_date <= (income["date"].split("T")[0] if "T" in income["date"] else income["date"]) <= end_date
            )
            
            # 计算完成度
            completion_rate = (total_income / goal["amount"]) * 100 if goal["amount"] > 0 else 0
            
            # 根据目标类型计算不同周期的完成度
            period_stats = {}
            if goal["period"] == "monthly":
                # 获取当月收入
                current_month = datetime.now().strftime("%Y-%m")
                monthly_income = sum(
                    income["amount"]
                    for income in incomes
                    if (income["date"].split("T")[0] if "T" in income["date"] else income["date"]).startswith(current_month)
                )
                period_stats["monthly"] = {
                    "current_amount": monthly_income,
                    "completion_rate": round((monthly_income / goal["amount"]) * 100, 2) if goal["amount"] > 0 else 0
                }
            elif goal["period"] == "yearly":
                # 获取当年收入
                current_year = datetime.now().strftime("%Y")
                yearly_income = sum(
                    income["amount"]
                    for income in incomes
                    if (income["date"].split("T")[0] if "T" in income["date"] else income["date"]).startswith(current_year)
                )
                period_stats["yearly"] = {
                    "current_amount": yearly_income,
                    "completion_rate": round((yearly_income / goal["amount"]) * 100, 2) if goal["amount"] > 0 else 0
                }
            
            progress.append({
                "goal": goal,
                "current_amount": total_income,
                "completion_rate": round(completion_rate, 2),
                "period_stats": period_stats
            })
        except Exception as e:
            logger.error(f"Error calculating progress for goal: {str(e)}")
            continue
    
    return progress

# 收入相关路由
@app.get("/api/incomes")
async def get_incomes():
    return read_json_file(INCOME_FILE)

@app.post("/api/incomes")
async def create_income(income: dict):
    try:
        incomes = read_json_file(INCOME_FILE)
        incomes.append(income)
        write_json_file(INCOME_FILE, incomes)
        return income
    except Exception as e:
        logger.error(f"Error creating income: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 