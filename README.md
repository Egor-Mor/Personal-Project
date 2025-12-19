# Pygame arcade

This repository hosts a personal web application built with **Flask**, designed to serve as a platform for various embedded web games created with pygame. It features user authentication system, a PostgreSQL/SQLite database backend, and is structured for easy deployment.

## ✨ Features

- **User Authentication:** Secure registration and login functionality using Flask-Login and password hashing with `werkzeug.security`.

- **Database Integration:** Utilizes Flask-SQLAlchemy with support for both SQLite (for development) and PostgreSQL (for production via `psycopg2-binary`).

- **Embedded Games:** A collection of simple, static web games (e.g., Pong, Snake, Tetris, Platformer) integrated into the application.

- **Comment System:** A basic comment and rating system linked to users and games, defined in the `Comment` model.

- **Modular Structure:** Clean separation of application logic, templates, and static assets.

- **Deployment Ready:** Configuration files (`vercel.json`, `gunicorn` in `requirements.txt`) are included for easy deployment to cloud platforms.

## 💻 Tech Stack

The project is built using the following core technologies:

| Category | Technology | Purpose |
| --- | --- | --- |
| **Backend Framework** | Python 3.x, Flask | Core web application framework. |
| **Database ORM** | Flask-SQLAlchemy | Object-Relational Mapper for database interactions. |
| **Authentication** | Flask-Login, Werkzeug | User session management and password hashing. |
| **Database Driver** | `Pyame, Pygbag` | PyGame and Pygbag are used to create games suitable for web-embedding. |
| **Web Server** | Gunicorn | Production WSGI HTTP Server. |  |

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

- Python 3.8+

- Git

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Egor-Mor/Personal-Project.git
   cd Personal-Project/app
   ```

1. **Create a virtual environment and activate it:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The application requires a few environment variables for secure and proper operation. Create a file named `.env` in the `Personal-Project/app` directory.

| Variable | Description | Example Value |
| --- | --- | --- |
| `SECRET_KEY` | A long, random string for session security. **REQUIRED.** | `my-super-secret-key-12345` |
| `DATABASE_URL` | The connection string for your database. | `sqlite:///instance/app.db` (for local SQLite ) |

**For local development (SQLite):** If `DATABASE_URL` is not set, the application will default to using a local SQLite database file at `instance/app.db`.

**For production (PostgreSQL):** Set `DATABASE_URL` to your PostgreSQL connection string, e.g.: `DATABASE_URL=postgresql://user:password@host:port/dbname`

### Running the Application

1. **Initialize the database:** The application will attempt to create the database tables on startup.

1. **Run in Development Mode:**

   ```bash
   export FLASK_APP=app.py
   flask run
   ```

   The application will be available at `http://127.0.0.1:5000/`.

1. **Run in Production Mode (using Gunicorn ):**

   ```bash
   gunicorn app:app
   ```

## 🎮 Embedded Games

The following games are included in the application and can be accessed via the web interface:

- **Game of Life**

- **Platformer**

- **Pong**

- **Snake**

- **Tetris**

- **Typing Test**

## 📂 Project Structure

The main application logic resides in the `app/` directory.

```
Personal-Project/
├── app/
│   ├── api/             # API endpoints (index.py)
│   ├── instance/        # Database files (app.db)
│   ├── static/          # Static assets (Images, games)
|   |   ├── img/         # Game previews, visible from homepage
│   │   └── Games/       # Source code and builds for embedded games
│   ├── templates/       # Jinja2 HTML templates
│   ├── app.py           # Main Flask application file
│   ├── models.py        # SQLAlchemy database models (User, Comment)
│   └── requirements.txt # Python dependencies
├── Mock_Project/        # Project to help understand me mechanics of frameworks and libraries
└── Diagrams/
```

