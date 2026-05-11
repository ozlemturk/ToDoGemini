# Handles todo pages, todo CRUD operations, and Gemini-powered todo description generation.
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from pydantic import BaseModel, Field
from starlette import status
from ..models import Base, Todo
from ..database import engine, SessionLocal
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Annotated
from ..routers.auth import get_current_user
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import markdown
from bs4 import BeautifulSoup

router = APIRouter(
    prefix = "/todo",
    tags = ["Todo"],
)

# Connects FastAPI with todo-related HTML templates.
templates = Jinja2Templates(directory="app/templates")

# Creates database tables if they do not already exist.
Base.metadata.create_all(bind=engine)

# Request model for creating and updating todos.
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=500)
    priority: int = Field(gt=0, lt=6)
    complete: bool



# Creates a database session for each request and closes it afterwards.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for database access.
db_dependency = Annotated[Session, Depends(get_db)]
# Dependency for accessing the currently authenticated user.
user_dependency = Annotated[dict, Depends(get_current_user)]

# Redirects unauthenticated users to the login page and removes the invalid token.
def redirect_to_login():
    redirect_response = RedirectResponse(url = "/auth/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response

# Renders the todo page and shows only the current user's todos.
@router.get("/todo-page")
async def render_todo_page(request:Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(Todo.owner_id == user.get("id")).all()
        return templates.TemplateResponse("todo.html",{"request":request, "todos":todos, "user":user})
    except:
        return redirect_to_login()


# Renders the add todo page.
@router.get("/add-todo-page")
async def render_add_todo_page(request:Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html",{"request":request, "user":user})
    except:
        return redirect_to_login()

# Renders the edit todo page for a specific todo.
@router.get("/edit-todo-page/{todo_id}")
async def render_todo_page(request:Request, todo_id:int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html",{"request":request, "todo":todo, "user":user})
    except:
        return redirect_to_login()


# Returns all todos that belong to the current user.
@router.get("/")
async def read_all(user:user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todo).filter(Todo.owner_id == user.get("id")).all()

# Returns a single todo by ID if it belongs to the current user.
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(user:user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get("id")).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

# Creates a new todo and improves its description using Gemini.
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,db: db_dependency, todo_request: TodoRequest):
    todo = Todo(**todo_request.dict(),owner_id = user.get("id"))
    # Generates a more detailed description before saving the todo.
    todo.description = create_todo_with_gemini(todo.description)
    db.add(todo)
    db.commit()

# Updates an existing todo if it belongs to the current user.
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get("id")).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.add(todo)
    db.commit()

# Deletes an existing todo.
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()

# Converts markdown content into plain text.
def markdown_to_text(markdown_string):
    html = markdown.markdown(markdown_string)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return text

# Uses Gemini to generate a longer and more practical todo description.
def create_todo_with_gemini(todo_string:str):
    load_dotenv()
    genai.configure(api_key = os.environ.get("GOOGLE_API_KEY"))
    llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")
    response = llm.invoke(
        [
            HumanMessage(content=f"""
    Create a longer and more comprehensive todo description for this todo item.

    Todo item: {todo_string}

    Write only the final todo description.
    Do not say "okay", "I understand", or "I'm ready".
    Make it practical and detailed.
    """)
        ]
    )

    return markdown_to_text(response.content)

# Allows testing the Gemini function directly from this file.
if __name__ == "__main__":
    print(create_todo_with_gemini("buy milk "))