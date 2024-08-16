from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="ah/ah_simple_home/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    agents = [agent for agent in os.listdir("data/agents/local") if os.path.isdir(os.path.join("data/agents/local", agent))]
    return templates.TemplateResponse("home.jinja2", {"request": request, "agents": agents})


