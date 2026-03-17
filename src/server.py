from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.main.routes import auth_routes, user_routes, view_routes, system_routes, quiz_routes

app = FastAPI(title="Adaptive Learning AI API")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(view_routes.router)
app.include_router(system_routes.router)
app.include_router(quiz_routes.router)