from fastapi import Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional

users = [
    {"id": 1, "username": "alice", "role": "user"},
    {"id": 2, "username": "bob", "role": "user"},
    {"id": 3, "username": "admin", "role": "admin"},
]

files_db: List[dict] = [
    {"id": 1, "name": "alice_report.pdf", "size": 123, "owner_id": 1,
     "original_name": "alice_report.pdf", "path": "storage/1_uuid.pdf"},
    {"id": 2, "name": "bob_notes.txt", "size": 456, "owner_id": 2,
     "original_name": "bob_notes.txt", "path": "storage/2_uuid.txt"},
    {"id": 3, "name": "admin_plan.docx", "size": 789, "owner_id": 3,
     "original_name": "admin_plan.docx", "path": "storage/3_uuid.docx"},
]


class User(BaseModel):
    id: int
    username: str
    role: str

def get_current_user(x_user_name: Optional[str] = Header(None)) -> User:
    if not x_user_name:
        raise HTTPException(status_code=401, detail="Missing X-User-Name header")
    for u in users:
        if u["username"] == x_user_name:
            return User(**u)
    raise HTTPException(status_code=401, detail="User not found")

def check_file_permissions(file_id: int, current_user: User = Depends(get_current_user)):
    from main import files_db
    for f in files_db:
        if f["id"] == file_id:
            if current_user.role == "admin" or f["owner_id"] == current_user.id:
                return f
            raise HTTPException(status_code=404, detail="Not Found")
    raise HTTPException(status_code=404, detail="Not Found")