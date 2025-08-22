from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for flash messages

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.name}>"

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/users")
def list_users():
    users = User.query.all()
    return render_template("users.html", users=users)

@app.route("/users/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("create_user"))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("create_user"))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {name} created successfully!", "success")
        return redirect(url_for("list_users"))
    return render_template("create_user.html")

@app.route("/users/update/<int:user_id>", methods=["GET", "POST"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.name = request.form.get("name")
        user.email = request.form.get("email")
        user.password = request.form.get("password")

        db.session.commit()
        flash(f"User {user.name} updated successfully!", "success")
        return redirect(url_for("list_users"))
    return render_template("update_user.html", user=user)

@app.route("/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.name} deleted successfully!", "success")
    return redirect(url_for("list_users"))

if __name__ == "__main__":
    app.run(debug=False)
