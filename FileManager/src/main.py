from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import bleach
from schemas import UserCreate
from dependencies import get_current_user, check_file_permissions

app = FastAPI()

templates = Jinja2Templates(directory="templates")
comments_store = []

files_db = [
    {"id": 1, "name": "alice_report.pdf", "size": 123, "owner_id": 1},
    {"id": 2, "name": "bob_notes.txt", "size": 456, "owner_id": 2},
    {"id": 3, "name": "admin_plan.docx", "size": 789, "owner_id": 3},
]

ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong']

def sanitize_comment(raw_text: str) -> str:
    return bleach.clean(
        raw_text,
        tags=ALLOWED_TAGS,
        attributes={},
        strip=True,
        strip_comments=True
    )

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self';"
        return response

app.add_middleware(CSPMiddleware)

@app.post("/registration")
def registration(user: UserCreate):
    return {"msg": "User created", "user": user.username}
@app.get("/comments", response_class=HTMLResponse)
async def get_comments(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments_store})

@app.post("/comments", response_class=HTMLResponse)
async def post_comment(request: Request, text: str = Form(...)):
    clean_text = sanitize_comment(text)
    comments_store.append(clean_text)
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments_store})

@app.get("/files/{file_id}")
def get_file(file_id: int, file = Depends(check_file_permissions)):
    return file

@app.delete("/files/{file_id}")
def delete_file(file_id: int, file = Depends(check_file_permissions)):
    global files_db
    files_db = [f for f in files_db if f["id"] != file_id]
    return {"msg": "Deleted", "file_id": file_id}

@app.get("/files/my")
def my_files(current_user: User = Depends(get_current_user)):
    return [f for f in files_db if f["owner_id"] == current_user.id]

@app.get("/files/all")
def all_files(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return files_db