#communication to the frontend requests
from datetime import datetime, timezone, time, timedelta
from zoneinfo import ZoneInfo
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, status

from app.authentication import (
    check_hashed_password,
    create_jwt_token,
    hash_password,
    make_formatted_userdata,
    validate_auth_user,
    validate_admin_user,
)
from app.database import energy_logs, tasks, users
from app.mana_engine import run_mana_engine
from app.fastapi_models import (
    AdminEnergyUpdate_model,
    AdminTaskCreate_model,
    EnergyLogCreate_model,
    TaskCreate_model,
    TaskUpdate_model,
    UserLogin_model,
    UserSignup_model,
)

est = ZoneInfo("America/New_York")
router = APIRouter()
#status checks





#authentication
@router.post("/authentication/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignup_model):
    if users.find_one({"username": payload.username.strip()}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    username = payload.username.strip()
    password = payload.password
    created_account = {
        "username": username,
        "hashed_pass": hash_password(password),
        "created_time": datetime.now(est),
        "current_energy": 0.0,
    }
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No username or password.")

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    jwt_token = create_jwt_token(str(user["_id"]))
    return {"access_token": jwt_token, "token_type": "bearer", "user": make_formatted_userdata(user)}


#dashboard
@router.get("/dashboard/summary")
def get_dashboard_summary(current_user: dict = Depends(validate_auth_user)):
    now = datetime.now(est)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    recurring_templates = list(
        tasks.find({
            "user_id": current_user["_id"],
            "is_recurring": True,
            "repeat_pattern": "daily",
            "is_generated_instance": False,
        })
    )
    
    for template in recurring_templates:
        og_time = template["scheduled_time"]
        todays_scheduled_time = datetime.combine(now.date(), time(og_time.hour, og_time.minute, og_time.second,), tzinfo=est,)
        if todays_scheduled_time < og_time:
            continue

        existing_instance = tasks.find_one({
            "user_id": current_user["_id"],
            "parent_task_id": template["_id"],
            "is_generated_instance": True,
            "scheduled_time": {"$gte": day_starttart, "$lte": day_endnd},
        })

        if not existing_instance:
            generated_task = {
                "user_id": current_user["_id"],
                "title": template["title"],
                "description": template.get("description", ""),
                "scheduled_time": todays_scheduled_time,
                "energy_cost": float(template.get("energy_cost", 0)),
                "actual_energy_cost": None,
                "status": "planned",
                "created_time": datetime.now(est),
                "updated_time": None,
                "completed_time": None,
                "is_recurring": False,
                "repeat_pattern": None,
                "parent_task_id": template["_id"],
                "is_generated_instance": True,
            }
            tasks.insert_one(generated_task)

    remaining_today_tasks = list(
        tasks.find({
            "user_id": current_user["_id"],
            "status": "planned",
            "scheduled_time": {"$gt": now, "$lte": day_end}, #will only consider tasks upcoming not completed
        })
    )

    remaining_today_endnergy_cost = round(
        sum(float(t.get("energy_cost", 0)) for t in remaining_today_tasks), 1
    )
    current_energy = round(float(current_user.get("current_energy", 0.0)), 1)
    estimated_end_of_day_endnergy = round(
        max(0.0, current_energy - remaining_today_endnergy_cost), 1
    )

    planned_tasks_count = tasks.count_documents({
        "user_id": current_user["_id"],
        "status": "planned",
    })
    completed_tasks_count = tasks.count_documents({
        "user_id": current_user["_id"],
        "status": "completed",
    })

    mana_extra = run_mana_engine(
        current_energy,
        remaining_today_endnergy_cost,
        estimated_end_of_day_endnergy,
        remaining_today_tasks,
    )
    max_energy = 10.0
    current_energy_percent = round((current_energy / max_energy) * 100.0, 1)
    estimated_end_energy_percent = round((estimated_end_of_day_endnergy / max_energy) * 100.0, 1)
    if current_energy <= 2.5:
        energy_bar_state = "low"
    elif current_energy <= 6.0:
        energy_bar_state = "medium"
    else:
        energy_bar_state = "high" #low cortisol fr
        
    return {
        "current_energy": current_energy,
        "remaining_today_endnergy_cost": remaining_today_endnergy_cost,
        "estimated_end_of_day_endnergy": estimated_end_of_day_endnergy,
        "planned_tasks_count": planned_tasks_count,
        "completed_tasks_count": completed_tasks_count,
        "remaining_today_tasks_amount": len(remaining_today_tasks),
        "energy_bar_state": energy_bar_state,
        "current_energy_percent": current_energy_percent,
        "estimated_end_energy_percent": estimated_end_energy_percent,
        "remaining_today_tasks": [_fmt_task(t) for t in remaining_today_tasks],
        "max_energy": max_energy,
        **mana_extra,
    }


def _fmt_energy_log(log: dict) -> dict:
    return {
        "id": str(log["_id"]),
        "energy_level": float(log["energy_level"]),
        "created_time": log["created_time"].isoformat(),
        "source": log.get("source", "manual"),
        "task_id": str(log["task_id"]) if log.get("task_id") else None,
    }


@router.post("/energy/log")
def log_energy(payload: EnergyLogCreate_model, current_user: dict = Depends(validate_auth_user)):
    energy_entry = {
        "user_id": current_user["_id"],
        "energy_level": float(payload.energy_level),
        "created_time": datetime.now(est),
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
        "actual_energy_cost": (
            float(task["actual_energy_cost"])
            if task.get("actual_energy_cost") is not None
            else None
        ),
        "created_time": task["created_time"].isoformat() if task.get("created_time") else None,
        "updated_time": task["updated_time"].isoformat() if task.get("updated_time") else None,
        "completed_time": task["completed_time"].isoformat() if task.get("completed_time") else None,
        "is_recurring": bool(task.get("is_recurring", False)),
        "repeat_pattern": task.get("repeat_pattern"),
        "parent_task_id": str(task["parent_task_id"]) if task.get("parent_task_id") else None,
        "is_generated_instance": bool(task.get("is_generated_instance", False)),
    }


@router.post("/tasks/create", status_code=status.HTTP_201_CREATED)
def add_task(
    payload: TaskCreate_model,
    current_user: dict = Depends(validate_auth_user),
):
    task = {
        "user_id": current_user["_id"],
        "title": payload.title.strip(),
        "description": payload.description.strip(),
        "scheduled_time": payload.scheduled_time,
        "energy_cost": float(payload.energy_cost),
        "actual_energy_cost": None,
        "status": "planned",
        "created_time": datetime.now(est),
        "updated_time": None,
        "completed_time": None,
        "is_recurring": bool(getattr(payload, "is_recurring", False)),
        "repeat_pattern": getattr(payload, "repeat_pattern", None),
        "parent_task_id": None,
        "is_generated_instance": False,
    }
    record = tasks.insert_one(task)
    task["_id"] = record.inserted_id
    return _fmt_task(task)


@router.get("/tasks")
def list_tasks(current_user: dict = Depends(validate_auth_user)):
    #planned_tasks = list(tasks.find({"status": "planned", "user_id": current_user["_id"]}))
    #completed_tasks = list(tasks.find({"status": "completed", "user_id": current_user["_id"]}))
    #user_tasks = list(tasks.find({"user_id": current_user["_id"]}))
    #return {"planned": [_fmt_task(t) for t in planned_tasks], "completed": [_fmt_task(t) for t in completed_tasks], "all": [_fmt_task(t) for t in all_user_tasks]}
    now = datetime.now(est)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    recurring_templates = list(
        tasks.find({
            "user_id": current_user["_id"],
            "is_recurring": True,
            "repeat_pattern": "daily",
            "is_generated_instance": False,
        })
    )
    for template in recurring_templates:
        og_time = template["scheduled_time"]
        todays_scheduled_time = datetime.combine(
            now.date(),
            time(
                og_time.hour,
                og_time.minute,
                og_time.second,
            ),
            tzinfo=est,
        )
        if todays_scheduled_time < og_time:
            continue
            
        past = tasks.find_one({
            "user_id": current_user["_id"],
            "parent_task_id": template["_id"],
            "is_generated_instance": True,
            "scheduled_time": {"$gte": day_start, "$lte": day_end},
        })

        if not past:
            generated_task = {
                "user_id": current_user["_id"],
                "title": template["title"],
                "description": template.get("description", ""),
                "scheduled_time": todays_scheduled_time,
                "energy_cost": float(template.get("energy_cost", 0)),
                "actual_energy_cost": None,
                "status": "planned",
                "created_time": datetime.now(est),
                "updated_time": None,
                "completed_time": None,
                "is_recurring": False,
                "repeat_pattern": None,
                "parent_task_id": template["_id"],
                "is_generated_instance": True,
            }
            tasks.insert_one(generated_task)

    user_tasks = list(
        tasks.find({"user_id": current_user["_id"]}).sort("scheduled_time", 1)
    )
    return {"tasks": [_fmt_task(t) for t in user_tasks]}

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

    if "title" in updates:
        updates["title"] = updates["title"].strip()
    if "description" in updates:
        updates["description"] = updates["description"].strip()
    if updates.get("is_recurring") is False:
        updates["repeat_pattern"] = None
    updates["updated_time"] = datetime.now(est)
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

    database_log = tasks.update_one(
        {"_id": ObjectId(task_id), "user_id": current_user["_id"]},
        {"$set": {"status": "completed", "completed_time": datetime.now(est), "updated_time": datetime.now(est)}},
    )
    if database_log.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated = tasks.find_one({"_id": ObjectId(task_id)})
    return _fmt_task(updated)


# admin endpoints
@router.get("/admin/users")
def admin_list_users(admin: dict = Depends(validate_admin_user)):
    all_users = list(users.find({}))
    return {"users": [make_formatted_userdata(u) for u in all_users]}


@router.get("/admin/users/{user_id}/schedule")
def admin_get_user_schedule(user_id: str, admin: dict = Depends(validate_admin_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    target = users.find_one({"_id": ObjectId(user_id)})
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_tasks = list(tasks.find({"user_id": ObjectId(user_id)}).sort("scheduled_time", 1))
    return {
        "user": make_formatted_userdata(target),
        "tasks": [_fmt_task(t) for t in user_tasks],
    }


@router.patch("/admin/users/{user_id}/energy")
def admin_update_user_energy(
    user_id: str,
    payload: AdminEnergyUpdate_model,
    admin: dict = Depends(validate_admin_user),
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"current_energy": float(payload.energy_level)}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    energy_logs.insert_one({
        "user_id": ObjectId(user_id),
        "energy_level": float(payload.energy_level),
        "created_time": datetime.now(est),
        "source": "admin",
    })

    updated = users.find_one({"_id": ObjectId(user_id)})
    return make_formatted_userdata(updated)


@router.post("/admin/users/{user_id}/tasks", status_code=status.HTTP_201_CREATED)
def admin_create_user_task(
    user_id: str,
    payload: AdminTaskCreate_model,
    admin: dict = Depends(validate_admin_user),
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    if not users.find_one({"_id": ObjectId(user_id)}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    task = {
        "user_id": ObjectId(user_id),
        "title": payload.title.strip(),
        "description": payload.description.strip(),
        "scheduled_time": payload.scheduled_time,
        "energy_cost": float(payload.energy_cost),
        "actual_energy_cost": None,
        "status": "planned",
        "created_time": datetime.now(est),
        "updated_time": None,
        "completed_time": None,
        "is_recurring": bool(payload.is_recurring),
        "repeat_pattern": payload.repeat_pattern,
        "parent_task_id": None,
        "is_generated_instance": False,
    }
    record = tasks.insert_one(task)
    task["_id"] = record.inserted_id
    return _fmt_task(task)


@router.patch("/admin/tasks/{task_id}")
def admin_update_task(
    task_id: str,
    payload: TaskUpdate_model,
    admin: dict = Depends(validate_admin_user),
):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    if "title" in updates:
        updates["title"] = updates["title"].strip()
    if "description" in updates:
        updates["description"] = updates["description"].strip()
    if updates.get("is_recurring") is False:
        updates["repeat_pattern"] = None
    updates["updated_time"] = datetime.now(est)

    result = tasks.update_one({"_id": ObjectId(task_id)}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated = tasks.find_one({"_id": ObjectId(task_id)})
    return _fmt_task(updated)


@router.delete("/admin/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_task(task_id: str, admin: dict = Depends(validate_admin_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID")

    result = tasks.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")



