# Main application file for the FastAPI project.
from fastapi import FastAPI,Request
from starlette.responses import RedirectResponse
from .models import Base,Todo
from fastapi.staticfiles import StaticFiles
from starlette import status
from .database import engine
from .routers.auth import router as auth_router
from .routers.todo import router as todo_router
import os

app = FastAPI()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")

# Mounts the static folder so CSS, JavaScript, and image files can be served.
app.mount("/static",StaticFiles(directory = st_abs_file_path),name = "static")

# Redirects the root URL to the todo page.
@app.get("/")
def read_root(request:Request):
    return RedirectResponse(url = "/todo/todo-page", status_code=status.HTTP_302_FOUND)

# Includes authentication routes.
app.include_router(auth_router)
# Includes todo routes.
app.include_router(todo_router)
# Creates database tables if they do not already exist.
Base.metadata.create_all(bind = engine)
