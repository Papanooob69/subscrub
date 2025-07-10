from fastapi import FastAPI
from app.routes import auth_routes
from app.routes.tool_routes import router as tool_router
from app.routes.report_routes import router as report_routes

app = FastAPI()

# app.include_router(tool_routes.router)

app.include_router(auth_routes.router)
app.include_router(tool_router)
app.include_router(report_routes)
