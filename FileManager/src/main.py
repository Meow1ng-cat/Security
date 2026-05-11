from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from schemas import UserCreate

app = FastAPI()

@app.post("/registration")
def registration(user: UserCreate):
    return {"msg": "User created", "user": user.username}

templates = Jinja2Templates(directory="templates")
comments_store = []

@app.get("/comments", response_class=HTMLResponse)
async def get_comments(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments_store})

@app.post("/comments", response_class=HTMLResponse)
async def post_comment(request: Request, text: str = Form(...)):
    comments_store.append(text)
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments_store})