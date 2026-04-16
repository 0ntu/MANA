#we need models for the inpuyts so that fastapi can auto validate them otherwise its a lotta code
# useful resource link: https://docs.pydantic.dev/latest/concepts/models/#generic-models
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, Literal
import re

def clean_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value

#handle requests
class UserSignup_model(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)
    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        value = clean_text(value)
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise ValueError(
                "Username may only contain letters, numbers, underscores, periods, and dashes"
            )
        return value


class UserLogin_model(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=1, max_length=128)
    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        return clean_text(value)



class TaskCreate_model(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    scheduled_time: datetime
    energy_cost: float = Field(..., ge=0.0, le=10.0)
    is_recurring: bool = False
    repeat_pattern: Optional[Literal["daily"]] = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return clean_text(value)
    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        return value.strip()
    @model_validator(mode="after")
    def validate_recurrence(self):
        if self.is_recurring and self.repeat_pattern != "daily":
            raise ValueError("Recurring tasks currently only support repeat_pattern='daily'")
        if not self.is_recurring and self.repeat_pattern is not None:
            raise ValueError("repeat_pattern requires is_recurring=True")
        return self


class TaskUpdate_model(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)
    scheduled_time: Optional[datetime] = None
    energy_cost: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    actual_energy_cost: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    is_recurring: Optional[bool] = None
    repeat_pattern: Optional[Literal["daily"]] = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return clean_text(value)
    @field_validator("description")
    @classmethod
    def clean_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()
    @model_validator(mode="after")
    def validate_recurrence(self):
        if self.is_recurring is False and self.repeat_pattern is not None:
            raise ValueError("repeat_pattern requires is_recurring=True")
        return self


class EnergyLogCreate_model(BaseModel):
    energy_level: float = Field(..., ge=0.0, le=10.0)


class AdminEnergyUpdate_model(BaseModel):
    energy_level: float = Field(..., ge=0.0, le=10.0)


class AdminTaskCreate_model(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    scheduled_time: datetime
    energy_cost: float = Field(..., ge=0.0, le=10.0)
    is_recurring: bool = False
    repeat_pattern: Optional[Literal["daily"]] = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return clean_text(value)

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_recurrence(self):
        if self.is_recurring and self.repeat_pattern != "daily":
            raise ValueError("Recurring tasks currently only support repeat_pattern='daily'")
        if not self.is_recurring and self.repeat_pattern is not None:
            raise ValueError("repeat_pattern requires is_recurring=True")
        return self
