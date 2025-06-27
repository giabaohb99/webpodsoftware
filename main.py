from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from core.core.config import settings
from core.core.database import engine, Base
# Import all models here so that Base has them registered
from users.models import *
from employee.models import *
from role.models import *
from story.models import *

from users.router import router as users_router
from employee.router import router as employee_router
from role.router import router as role_router
from story.router import router as story_router
from file_storage.router import router as file_storage_router

from core.core.exceptions import APIError
from core.core.exception_handlers import api_error_handler, request_validation_error_handler, generic_error_handler
from fastapi.exceptions import RequestValidationError

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    exception_handlers={
        APIError: api_error_handler,
        RequestValidationError: request_validation_error_handler,
        Exception: generic_error_handler,
    }
)

# Add HTTPS Redirect Middleware if enabled
if settings.ENABLE_SSL:
    app.add_middleware(HTTPSRedirectMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you should restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from different modules
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(employee_router, prefix=settings.API_V1_STR)
app.include_router(role_router, prefix=settings.API_V1_STR)
app.include_router(story_router, prefix=settings.API_V1_STR)
app.include_router(file_storage_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to the application!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 