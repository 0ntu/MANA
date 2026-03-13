#communication to the frontend requests
"""
API ROUTES

This file defines the main FastAPI endpoints used.
It connects the Streamlit frontend to the MongoDB database and handles
core features such as authentication, energy logging, task management,
and dashboard calculations.
"""

from app.database import users, energy_logs, tasks
from app.authentication import hashingUtil, make_formatted_userdata, create_jwt_token, validate_auth_user, check_hashed_password
from app.fastapi_models import UserSignup_model, UserLogin_model, TaskCreate_model, TaskUpdate_model, EnergyLogCreate_model
from fastapi import status, HTTPException, APIRouter
from bsonimport ObjectId
from datetime import datetime, timezone

router = APIRouter()
#status checks

def make_formatted_energylog(log: dict) -> dict:

def make_formatted_task(log: dict) -> dict:


#authentication
@router.post("/authentication/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignup_model):
  if (users.find_one({"username": payload.username})):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username entered already exists")
  
  created_account = {"username": payload.username.strip(), "hashed_pass": hash_password(payload.password), "timestamp": datetime.now(timezone.est), "current_energy": 0.0}
  
  database_record = users.insert_one(created_account)
  accountID = users.find_one({"_id": database_record.inserted_id})
  jwt_token = create_jwt_token(str(result.inserted_id))

  return {"jwt_token": jwt_token, "token_type": "bearer", "user": make_formatted_uerdata(accountID)}

@router.post("/authentication/login")
def login(payload: UserLogin_model):
  user = users.find_one({"username": payload.username.strip()})
  if not (check_hashed_password(payload.password, user["hashed_pass"]) and user):
    raise HTTPException(status_code=status.HTTP_400_UNAUTHORIZED, detail="Bad login")
  jwt_token = create_jwt_token(str(user["_id"]))
  return {"access_token": access_token, "token_type": "bearer", "user": make_formatted_userdata(user)}


#dashboard
@router.get("/dashboard/summary")
def get_dashboard_summary(current_user: dict = Depends(validate_auth_user)):
  time = datetime.now(timezone.est)
  daystart = time.replace(hour=0, minute=0, second=0)
  
  remaining_today_tasks = list(tasks.find({"user_id": current_user["_id"], "status": "planned", "scheduled_for": {}})) #need to develop more
  
  remaining_today_energy_cost = round(sum(float(task["estimated_energy_cost"]) for task in remaining_today_tasks), 1) #ensure float
  current_energy = round(float(current_user.get("current_energy", 0.0)), 1)
  estimated_end_of_day_energy = round(max(0.0, current_energy - remaining_today_energy_cost), 1)
  
  planned_tasks_count = tasks.count_documents({"user_id": current_user["_id"], "status": "completed"})
  completed_tasks_count = tasks.count_documents({"user_id": current_user["_id"], "status": "completed"})

  return {"remaining_today_energy_cost": remaining_today_energy_cost, "current_energy": current_energy, "estimated_end_of_day_energy": estimated_end_of_day_energy, "planned_tasks_count": planned_tasks_count, "completed_tasks_count": completed_tasks_count,"remaining_today_tasks_amount": len(remaining_today_tasks)} 


#energy


#tasks


  
