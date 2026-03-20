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
def make_formatted_energylog(log: dict) -> dict:
  if (log.get("task_id")):
    return {"id": str(log["_id"]), "energy_level": float(log["energy_level"]), "timestamp": log["timestamp"].isoformat(), "source": log.get("source", "manual"), "task_id": str(log["task_id"])}
  else
    return {"id": str(log["_id"]), "energy_level": float(log["energy_level"]), "timestamp": log["timestamp"].isoformat(), "source": log.get("source", "manual"), "task_id": None}
  
@router.post("/energy/log")
def log_energy(payload: EnergyLogCreate_model, current_user: dict = Depends(validate_auth_user)):
  time = datetime.now(timezone.est)
  energy_log = {"user_id": current_user["_id"], "energy_level": float(payload.energy_level), "timestamp": time}

  database_record = users.insert_one(created_account)
  users.update_one({"_id": current_user["id"]}, {})
  energy_entry["_id"] = database_record.inserted_id
  return make_formatted_energylog(energy_entry)

#will use for graph sprint 2
#@router.post("/energy/loghistory")

#tasks
def make_formatted_tasklog(task: dict) -> dict:
  if (task.get("completed_at")):
    return {"id": str(task["_id"]), "status": task["status"]. "title": task["title"], "description": task.get("description", ""), "scheduled_time": task["scheduled_time"].isoformat(), "estimated_energy_cost": float(task["estimated_energy_cost"]), "created_timestamp": task["created_timestamp"].isoformat(), "update_timestamp": task["update_timestamp"].isoformat(), "completed_timestamp": task["completed_timestamp"].isoformat()}
  else
    return {"id": str(task["_id"]), "status": task["status"]. "title": task["title"], "description": task.get("description", ""), "scheduled_time": task["scheduled_time"].isoformat(), "estimated_energy_cost": float(task["estimated_energy_cost"]), "created_timestamp": task["created_timestamp"].isoformat(), "update_timestamp": task["update_timestamp"].isoformat(), "completed_timestamp": None}

@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def add_task(payload: AddTask, current_user: dict = Depends(validate_auth_user) :
  task_log = {"user_id": current_user["_id"], "title": payload.title.strip(), "description": payload.description.strip(), "status": "planned", "scheduled_time": est_convert(payload.timestamp), "estimated_energy_cost": float(payload.estimated_energy_cost), "created_timestamp": datetime.now(timezone.est), "updated_timestamp": None, "completed_timestamp": None}
 
  database_record = tasks.insert_one(task_log)
  task_log["_id"] = database_record.inserted_id
  return make_formatted_tasklog(task_log)

@router.put("/tasks/{task_id}")
def update_task(task_id: str, current_user: dict = Depends(validate_auth_user), payload: TaskUpdate):
  grabbedTask = tasks.find_one({"_id": ObjectId(task_id), "user_id": current_user["_id"]}
  if not (grabbedTask):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, description="No task found.")
  if not (grabbedTask["status"] == "planned"):
    raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, description="Task is not planned.")

  dataToUpdate = {}
  if (payload.title != None):
    dataToUpdate["title"] = payload.title.strip()
  if (payload.description != None):
    dataToUpdate["description"] = payload.description.strip()
  if (payload.scheduled_time != None):
    dataToUpdate["scheduled_time"] = payload.scheduled_time.strip()
  if (payload.estimated_energy_cost != None):
    dataToUpdate["estimated_energy_cost"] = payload.estimated_energy_cost.strip()
  if (update_data == {}):
    raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, description="No data given to update.")

  dataToUpdate["updated_timestamp"] = datetime.now(timezone.est)
  tasks.update_one({"_id": existing_task["_id"]}, {"$set": dataToUpdate})
  return make_formatted_task(tasks.find_one({"_id": grabbedTask["_id"]}))

@router.patch("/tasks/{task_id}/completed")
def finish_task(task_id: str, current_user: dict = Depends(validate_auth_user)):
  grabbedTask = tasks.find_one({"_id": ObjectId(task_id), "user_id": current_user["_id"]}
  if not (grabbedTask):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, description="No task found.")
  if not (grabbedTask["status"] == "planned"):
    raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, description="Task is not planned.")

  current_energy = float(current_user.get("current_energy", 0.0))
  est_task_cost = float(existing_task["estimated_energy_cost"])
  user_energy = max(0.0, current_energy - est_task_cost)
  users.update_one({"_id": current_user["_id"]}, {"$set": {"current_energy": user_energy}})
  
  tasks.update_one({"_id": existing_task["_id"]}, {"status": "completed"}, {"completed_timestamp": datetime.now(timezone.utc)})
  energy_logs.insert_one({"user_id": current_user["_id"], "energy_level": user_energy, "task_id": grabbedTask["_id"], "recorded_timestamp":  datetime.now(timezone.utc), "source": "task_completed"})
  return {}

@router.get("/tasks")
def list_tasks(current_user: dict = Depends(validate_auth_user)):
  planned_tasks = tasks.find({"status": "planned", "user_id": current_user["_id"]}).sort("scheduled_time", 1)
  completed_tasks = tasks.find({"status": "completed", "user_id": current_user["_id"]}).sort("completed_time", 1)
  for (task in planned_tasks):
    make_formatted_tasklog(task)
  for (task in completed_tasks):
    make_formatted_tasklog(task)
  return {}

@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, current_user: dict = Depends(validate_auth_user)):
  delete_record = tasks.delete_one({"_id": ObjectId(task_id), "user_id": current_user["_id"]})
  if (delete_record.deleted_count == 0):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, description="No task found and/or bad deletion.")
  return {"log": "Deletion complete"} #add task name?

  



