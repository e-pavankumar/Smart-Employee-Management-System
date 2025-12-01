📘 Smart Employee Management System

A simple and efficient web application built using Python (Flask) and SQLite to manage employees, assign tasks, and view organizational insights. The system includes Signup/Login, Employee CRUD, Task Management, and a clean Dashboard UI suitable for demonstrating full-stack development skills for an Associate Software Engineer role.

🚀 Features
🔐 Authentication

User Signup

User Login

Secure password hashing

Session-based authentication

👤 Employee Management

Add new employees

Edit employee information

Delete employees

View employees in a tabular format

📝 Task Management

Create tasks

Assign tasks to employees

Update task status

Delete tasks

📊 Dashboard

Displays key statistics:

Total Employees

Total Tasks

Completed Tasks

(No pie charts included — simple stat cards only.)

🗃 Database

Uses SQLite + SQLAlchemy ORM for easy portability.

🏗 Tech Stack
Layer	Technology
Backend	Python, Flask
Frontend	HTML, Bootstrap
Database	SQLite (SQLAlchemy ORM)
Authentication	Werkzeug password hashing
Templating	Jinja2

📂 Project Structure
smart_ems/
│── app.py
│── requirements.txt
│── templates/
│     ├── base.html
│     ├── login.html
│     ├── signup.html
│     ├── dashboard.html
│     ├── employees.html
│     ├── employee_form.html
│     ├── tasks.html
│     └── task_form.html
│── static/
      └── style.css




▶️ How to Run
git clone <repo_url>
cd smart_ems

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python app.py


Open in browser:
👉 http://127.0.0.1:5000/login

🙌 Author

Pavan
Aspiring Associate Software Engineer | Python Developer# Smart-Employee-Management-System
