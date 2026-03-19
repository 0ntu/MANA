#communication to the frontend requests
"""
API ROUTES

This file defines the main FastAPI endpoints used.
It connects the Streamlit frontend to the MongoDB database and handles
core features such as authentication, energy logging, task management,
and dashboard calculations.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.authentication import (
    check_hashed_password,
    create_jwt_token,
    hash_password,
    make_formatted_userdata,
    validate_auth_user,
)
from app.database import energy_logs, tasks, users
from app.fastapi_models import (
    EnergyLogCreate_model,
    TaskCreate_model,
    TaskUpdate_model,
    UserLogin_model,
    UserSignup_model,
)

router = APIRouter()
#status checks


#authentication
@router.post("/authentication/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignup_model):
    if users.find_one({"username": payload.username.strip()}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    now = datetime.now(timezone.utc)
    created_account = {
        "username": payload.username.strip(),
        "hashed_pass": hash_password(payload.password),
        "created_at": now,
        "current_energy": 0.0,
    }

    record = users.insert_one(created_account)
    user_doc = users.find_one({"_id": record.inserted_id})
    jwt_token = create_jwt_token(str(record.inserted_id))

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": make_formatted_userdata(user_doc),
    }


@router.post("/authentication/login")
def login(payload: UserLogin_model):
    user = users.find_one({"username": payload.username.strip()})
    if not user or not check_hashed_password(payload.password, user["hashed_pass"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    jwt_token = create_jwt_token(str(user["_id"]))
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": make_formatted_userdata(user),
    }


#dashboard
@router.get("/dashboard/summary")
def get_dashboard_summary(current_user: dict = Depends(validate_auth_user)):
    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    remaining_today_tasks = list(
        tasks.find({
            "user_id": current_user["_id"],
            "status": "planned",
            "scheduled_time": {"$gte": day_start, "$lte": day_end},
        })
    )

    remaining_today_energy_cost = round(
        sum(float(t.get("energy_cost", 0)) for t in remaining_today_tasks), 1
    )
    current_energy = round(float(current_user.get("current_energy", 0.0)), 1)
    estimated_end_of_day_energy = round(
        max(0.0, current_energy - remaining_today_energy_cost), 1
    )

    planned_tasks_count = tasks.count_documents({
        "user_id": current_user["_id"],
        "status": "planned",
    })
    completed_tasks_count = tasks.count_documents({
        "user_id": current_user["_id"],
        "status": "completed",
    })

    return {
        "current_energy": current_energy,
        "remaining_today_energy_cost": remaining_today_energy_cost,
        "estimated_end_of_day_energy": estimated_end_of_day_energy,
        "planned_tasks_count": planned_tasks_count,
        "completed_tasks_count": completed_tasks_count,
        "remaining_today_tasks_amount": len(remaining_today_tasks),
    }


def _fmt_energy_log(log: dict) -> dict:
    return {
        "id": str(log["_id"]),
        "energy_level": float(log["energy_level"]),
        "timestamp": log["timestamp"].isoformat(),
        "source": log.get("source", "manual"),
        "task_id": str(log["task_id"]) if log.get("task_id") else None,
    }


@router.post("/energy/log")
def log_energy(
    payload: EnergyLogCreate_model,
    current_user: dict = Depends(validate_auth_user),
):
    now = datetime.now(timezone.utc)
    energy_entry = {
        "user_id": current_user["_id"],
        "energy_level": float(payload.energy_level),
        "timestamp": now,
        "source": "manual",
    }

    record = energy_logs.insert_one(energy_entry)
    users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"current_energy": float(payload.energy_level)}},
    )
    energy_entry["_id"] = record.inserted_id
    return _fmt_energy_log(energy_entry)


#will use for graph sprint 2
#@router.post("/energy/loghistory")

#tasks
def _fmt_task(task: dict) -> dict:
    return {
        "id": str(task["_id"]),
        "status": task["status"],
        "title": task["title"],
        "description": task.get("description", ""),
        "scheduled_time": task["scheduled_time"].isoformat(),
        "energy_cost": float(task.get("energy_cost", 0)),
        "created_at": task["created_at"].isoformat(),
        "updated_at": task["updated_at"].isoformat(),
        "completed_at": task["completed_at"].isoformat() if task.get("completed_at") else None,
    }


@router.post("/tasks/create", status_code=status.HTTP_201_CREATED)
def add_task(
    payload: TaskCreate_model,
    current_user: dict = Depends(validate_auth_user),
):
    now = datetime.now(timezone.utc)
    task = {
        "user_id": current_user["_id"],
        "title": payload.title,
        "description": payload.description,
        "scheduled_time": payload.scheduled_time,
        "energy_cost": float(payload.energy_cost),
        "status": "planned",
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
    }
    record = tasks.insert_one(task)
    task["_id"] = record.inserted_id
    return _fmt_task(task)


@router.get("/tasks")
def list_tasks(current_user: dict = Depends(validate_auth_user)):
    user_tasks = list(tasks.find({"user_id": current_user["_id"]}))
    return [_fmt_task(t) for t in user_tasks]


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: str,
    payload: TaskUpdate_model,
    current_user: dict = Depends(validate_auth_user),
):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updates["updated_at"] = datetime.now(timezone.utc)
    result = tasks.update_one(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]},
        {"$set": updates},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated = tasks.find_one({"_id": ObjectId(task_id)})
    return _fmt_task(updated)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, current_user: dict = Depends(validate_auth_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")

    result = tasks.delete_one({"_id": ObjectId(task_id), "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.post("/tasks/{task_id}/finish")
def finish_task(task_id: str, current_user: dict = Depends(validate_auth_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")

    now = datetime.now(timezone.utc)
    result = tasks.update_one(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]},
        {"$set": {"status": "completed", "completed_at": now, "updated_at": now}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated = tasks.find_one({"_id": ObjectId(task_id)})
    return _fmt_task(updated)
