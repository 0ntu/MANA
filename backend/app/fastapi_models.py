#we need models for the inpuyts so that fastapi can auto validate them otherwise its a lotta code
# useful resource link: https://docs.pydantic.dev/latest/concepts/models/#generic-models
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


#handle requests
class UserSignup_model(BaseModel):
    username: str
    password: str

class UserLogin_model(BaseModel):
    username: str
    password: str


class TaskCreate_model(BaseModel):
    title: str
    description: str = ""
    scheduled_time: datetime
    energy_cost: float


class TaskUpdate_model(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    energy_cost: Optional[float] = None


class EnergyLogCreate_model(BaseModel):
    energy_level: float = Field(..., ge=0.0, le=10.0)
