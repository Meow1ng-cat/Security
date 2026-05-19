import uuid
import os
import aiofiles
from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File as FastAPIFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
import filetype
import bleach
from schemas import UserCreate
from dependencies import files_db, get_current_user, check_file_permissions, User
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY not set in .env")
cipher = Fernet(FERNET_KEY.encode())

MAX_FILE_SIZE = 2 * 1024 * 1024
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]
UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

templates = Jinja2Templates(directory="templates")
comments_store = []

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

@app.get("/files/my")
def my_files(current_user: User = Depends(get_current_user)):
    return [f for f in files_db if f["owner_id"] == current_user.id]

@app.get("/files/all")
def all_files(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return files_db
@app.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    file_meta: dict = Depends(check_file_permissions)
):
    file_path = file_meta["path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    async with aiofiles.open(file_path, "rb") as f:
        data = await f.read()

    if file_meta.get("is_encrypted", False):
        try:
            decrypted_data = cipher.decrypt(data)
        except Exception:
            raise HTTPException(status_code=500, detail="Decryption failed")
        return_response_data = decrypted_data
    else:
        return_response_data = data

    return Response(
        content=return_response_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=\"{file_meta['original_name']}\""}
    )
@app.get("/files/{file_id}")
def get_file(file_id: int, file = Depends(check_file_permissions)):
    return file

@app.delete("/files/{file_id}")
def delete_file(file_id: int, file = Depends(check_file_permissions)):
    files_db[:] = [f for f in files_db if f["id"] != file_id]   # изменяем существующий список
    return {"msg": "Deleted", "file_id": file_id}

@app.post("/files/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    encrypt: bool = False
):
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 2 MB)")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    kind = filetype.guess(content)
    if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG/PNG images allowed")

    ext = ".jpg" if kind.mime == "image/jpeg" else ".png"
    new_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    if encrypt:
        encrypted_data = cipher.encrypt(content)
        data_to_save = encrypted_data
    else:
        data_to_save = content

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(data_to_save)

    new_id = max([f["id"] for f in files_db]) + 1 if files_db else 1
    file_meta = {
        "id": new_id,
        "name": new_filename,
        "original_name": file.filename,
        "size": len(content),
        "owner_id": current_user.id,
        "path": file_path,
        "is_encrypted": encrypt
    }
    files_db.append(file_meta)
    return {"msg": "File uploaded", "file_id": new_id, "original_name": file.filename, "encrypted": encrypt}
