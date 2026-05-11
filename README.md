# ToDoGemini

AI-powered Todo application built with FastAPI, Gemini, SQLAlchemy, JWT authentication, and Jinja2 templates.

## Overview

ToDoGemini is a full-stack todo management application that allows users to:

- Register and log in securely
- Create, update, and delete todos
- Manage personal todo lists
- Generate more detailed and practical todo descriptions using Google Gemini AI

This project was developed while learning FastAPI and AI integrations.

---

## Features

- JWT Authentication
- User Registration & Login
- Password Hashing with bcrypt
- Todo CRUD Operations
- User-specific Todos
- Gemini AI Integration
- SQLAlchemy ORM
- Alembic Database Migrations
- Jinja2 Templates
- SQLite Database

---

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- Alembic

### Authentication
- JWT
- Passlib
- bcrypt

### AI Integration
- Google Gemini
- LangChain

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Database
- SQLite

---

## Project Structure

```text
ToDoGemini/
│
├── alembic/
├── routers/
│   ├── auth.py
│   ├── todo.py
│   └── __init__.py
│
├── static/
├── templates/
│
├── database.py
├── models.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/ozlemturk/ToDoGemini.git
```

Go to the project directory:

```bash
cd ToDoGemini
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_secret_key_here
```

Run the application:

```bash
uvicorn main:app --reload
```

---

## API Documentation

FastAPI automatically generates API documentation:

- Swagger UI:
`http://127.0.0.1:8000/docs`

- ReDoc:
`http://127.0.0.1:8000/redoc`

---

## What I Learned

While building this project, I practiced:

- FastAPI routing
- JWT authentication
- Password hashing
- SQLAlchemy ORM
- Alembic migrations
- AI integration with Gemini
- LangChain basics
- CRUD operations
- Template rendering with Jinja2

---

## Future Improvements

- PostgreSQL integration
- Docker support
- Deployment with Render or Railway
- Email verification
- Better AI prompt engineering
- Unit tests
- Responsive frontend improvements

---

## Credits and Disclaimer

This project was developed for educational purposes while following backend and AI development tutorials and courses, including content from :contentReference[oaicite:0]{index=0}.

Some project structure and implementation ideas were inspired by tutorial-based learning materials. The project was customized and extended with Gemini AI integration and additional backend features as part of the learning process.

---

## License

This project is licensed under the MIT License.
