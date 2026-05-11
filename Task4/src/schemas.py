from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
import re


class UserCreate(BaseModel):
    username: str = Field(pattern=r"^[A-Za-z0-9]{4,20}$")
    email: EmailStr
    password: str
    confirm_password: str
    age: int = Field(ge=18, le=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*]", value):
            raise ValueError("Password must contain at least one special symbol")
        return value

    @model_validator(mode="after")
    def check_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self