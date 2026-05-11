from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import bleach
from schemas import UserCreate

app = FastAPI()

@app.post("/registration")
def registration(user: UserCreate):
    return {"msg": "User created", "user": user.username}

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

@app.get("/comments", response_class=HTMLResponse)
async def get_comments(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments_store})

@app.post("/comments", response_class=HTMLResponse)
async def post_comment(request: Request, text: str = Form(...)):
    clean_text = sanitize_comment(text)
    comments_store.append(clean_text)
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments_store})