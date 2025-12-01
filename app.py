from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ems.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------ MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20), default="user")

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    department = db.Column(db.String(80))
    role = db.Column(db.String(80))
    location = db.Column(db.String(80))
    date_joined = db.Column(db.Date, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="employee", lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default="Pending")
    due_date = db.Column(db.Date)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"))

# ------------------ LOGIN HELPERS ------------------

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap

# ------------------ AUTH ROUTES ------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("signup"))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["username"] = user.username
        flash("Login successful!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------ DASHBOARD ------------------

@app.route("/")
@login_required
def dashboard():
    total_employees = Employee.query.count()
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status="Completed").count()

    # Employees by department
    dept_data = (
        db.session.query(Employee.department, db.func.count(Employee.id))
        .group_by(Employee.department)
        .all()
    )
    departments = [d[0] if d[0] else "Unknown" for d in dept_data]
    dept_counts = [d[1] for d in dept_data]

    # Tasks by status
    status_data = (
        db.session.query(Task.status, db.func.count(Task.id))
        .group_by(Task.status)
        .all()
    )
    statuses = [s[0] for s in status_data]
    status_counts = [s[1] for s in status_data]

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        departments=departments,
        dept_counts=dept_counts,
        statuses=statuses,
        status_counts=status_counts,
    )

# ------------------ EMPLOYEES CRUD ------------------

@app.route("/employees")
@login_required
def employees():
    emp_list = Employee.query.all()
    return render_template("employees.html", employees=emp_list)


@app.route("/employees/new", methods=["GET", "POST"])
@login_required
def new_employee():
    if request.method == "POST":
        emp = Employee(
            full_name=request.form["full_name"],
            email=request.form["email"],
            department=request.form["department"],
            role=request.form["role"],
            location=request.form["location"],
            date_joined=datetime.strptime(request.form["date_joined"], "%Y-%m-%d")
        )
        db.session.add(emp)
        db.session.commit()
        flash("Employee added!", "success")
        return redirect(url_for("employees"))

    return render_template("employee_form.html", employee=None)


@app.route("/employees/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_employee(id):
    emp = Employee.query.get_or_404(id)

    if request.method == "POST":
        emp.full_name = request.form["full_name"]
        emp.email = request.form["email"]
        emp.department = request.form["department"]
        emp.role = request.form["role"]
        emp.location = request.form["location"]
        emp.date_joined = datetime.strptime(request.form["date_joined"], "%Y-%m-%d")

        db.session.commit()
        flash("Employee updated!", "success")
        return redirect(url_for("employees"))

    return render_template("employee_form.html", employee=emp)


@app.route("/employees/<int:id>/delete", methods=["POST"])
@login_required
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employee deleted!", "info")
    return redirect(url_for("employees"))

# ------------------ TASKS CRUD ------------------

@app.route("/tasks")
@login_required
def tasks():
    tasks = Task.query.all()
    employees = Employee.query.all()
    return render_template("tasks.html", tasks=tasks, employees=employees)


@app.route("/tasks/new", methods=["GET", "POST"])
@login_required
def new_task():
    employees = Employee.query.all()

    if request.method == "POST":
        due_date = request.form["due_date"]
        due_date = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None

        t = Task(
            title=request.form["title"],
            description=request.form["description"],
            status=request.form["status"],
            employee_id=request.form["employee_id"],
            due_date=due_date
        )
        db.session.add(t)
        db.session.commit()
        flash("Task created!", "success")
        return redirect(url_for("tasks"))

    return render_template("task_form.html", task=None, employees=employees)


@app.route("/tasks/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    employees = Employee.query.all()

    if request.method == "POST":
        task.title = request.form["title"]
        task.description = request.form["description"]
        task.status = request.form["status"]
        due_date = request.form["due_date"]
        task.due_date = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
        task.employee_id = request.form["employee_id"]

        db.session.commit()
        flash("Task updated!", "success")
        return redirect(url_for("tasks"))

    return render_template("task_form.html", task=task, employees=employees)


@app.route("/tasks/<int:id>/delete", methods=["POST"])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted!", "info")
    return redirect(url_for("tasks"))

# ------------------ INIT DB ------------------

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
