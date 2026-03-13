#we need models for the inpuyts so that fastapi can auto validate them otherwise its a lotta code
# useful resource link: https://docs.pydantic.dev/latest/concepts/models/#generic-models
from pydantic import BaseModel
from datetime import datetime

#handle requests
class Signup_model(BaseModel):
  username:str
  password:str

class Login_model(BaseModel):
  username:str
  password:str

class CreateTask_model(BaseModel):
  title: str
  description: str = ""
  scheduled_time: datetime
  energy_cost: float

class UpdateTask_model(BaseModel):
  title: str | None = None
  scheduled_time: datetime | None = None
  energy_cost: float | None = None

class EnergyLog_model(BaseModel):
  energy_level = float

