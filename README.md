# SubScrub – SaaS Backend for Tool Usage & Employee Tracking

SubScrub is a FastAPI-based backend system for managing tools, assigning them to employees, and tracking usage to detect inactive users.

## 🧰 Tech Stack

- **FastAPI** – Python backend framework
- **PostgreSQL** – Relational database
- **SQLAlchemy + Alembic** – ORM + migrations
- **Pydantic** – Schema validation
- **JWT Authentication** – Secure login system

---

## 🔐 Features

### 1. User Authentication
- Register & login with JWT token issuance
- All routes are protected using current user context

### 2. Tool Management
- Create, list, update, and delete tools (per user ownership)

### 3. Tool Assignment
- Assign tools to employees
- Track assignment date and last usage

### 4. Tool Usage Tracking
- Employees mark tools as used
- Tracks last usage per employee per tool

### 5. Inactive Employee Detection
- Detects employees who:
  - Haven’t used any tool in 30+ days
  - Or are unassigned

---

## 📦 Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/subscrub-backend.git
cd subscrub-backend
Create Virtual Environment
pip install -r requirements.txt
Configure Database
Run Migrations
Start the Server


