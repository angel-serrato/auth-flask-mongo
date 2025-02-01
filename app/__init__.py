import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    logout_user,
    login_user,
    current_user,
)
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo, MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
from flask_wtf.csrf import CSRFProtect
from bson import ObjectId
from pymongo.errors import ConnectionFailure
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")

bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
mongo = PyMongo(app, tls=True, tlsAllowInvalidCertificates=True)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

try:
    client = MongoClient(os.getenv("MONGO_URI"))
    client.admin.command("ping")
    print("Conexion exitosa a mongodb atlas")
except ConnectionFailure:
    print("Error de conexion")
except Exception as e:
    print(f"Error inesperado: {e}")


class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

    @staticmethod
    def get(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data["_id"], user_data["email"])
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    """
    Ruta principal del sitio. Renderiza la página de inicio.

    Returns:
        str: HTML de la página de inicio.
    """
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Ruta de inicio de sesión. Maneja tanto la visualización del formulario de login
    como la validación de las credenciales del usuario.

    Returns:
        str: HTML de la página de login.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user_data = mongo.db.users.find_one({"email": email})
        if user_data and bcrypt.check_password_hash(user_data["password"], password):
            user = User(user_data["_id"], user_data["email"])
            login_user(user)
            flash("Logged in successfully. Welcome back!", "info")
            return redirect(url_for("admin"))
        else:
            flash("Invalid email or password. Try again!", "danger")
            return redirect(url_for("login"))
    return render_template("auth/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Ruta para registrar a un nuevo usuario. Valida los datos y crea una cuenta,
    enviando un correo de bienvenida.

    Returns:
        str: HTML del formulario de registro.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if mongo.db.users.find_one({"email": email}):
            flash("Email already has an account.", "danger")
            return redirect(url_for("register"))
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = {
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        mongo.db.users.insert_one(user)
        msg = Message(
            "Welcome to Serrato Dev.",
            sender="angeldidierserratoarias@gmail.com",
            recipients=[email],
        )
        msg.html = render_template("emails/welcome.html")
        mail.send(msg)
        # user_id = result.inserted_id
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("auth/register.html")


@app.route("/admin")
@login_required
def admin():
    """
    Ruta para acceder al área de administración. Muestra los datos del usuario
    autenticado.

    Returns:
        str: HTML de la página de administración.
    """
    user_data = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
    if user_data:
        email = user_data["email"]
        password_hash = user_data["password"]
        created_at = user_data["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return render_template(
            "admin.html",
            email=email,
            password_hash=password_hash,
            created_at=created_at,
        )
    else:
        flash("User not found.", "danger")
        return redirect(url_for("login"))


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """
    Ruta para la recuperación de contraseña. Solicita un correo y, si el correo existe,
    envía un enlace de recuperación.

    Returns:
        str: HTML de la página de recuperación de contraseña.
    """
    if request.method == "POST":
        email = request.form["email"]
        user = mongo.db.users.find_one({"email": email})
        if user:
            token = serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])
            reset_url = url_for("reset_password", token=token, _external=True)
            msg = Message(
                "Recuperacion de contraseña",
                sender="angeldidierserratoarias@gmail.com",
                recipients=[email],
            )
            msg.html = render_template(
                "emails/reset_password.html", reset_url=reset_url
            )
            mail.send(msg)
            flash(
                "Se ha enviado un correo electrónico para reestablecer tu contraseña.",
                "info",
            )
            return redirect(url_for("login"))
        else:
            flash("No existe una cuenta asociada a ese correo electrónico.", "danger")
    return render_template("auth/forgot.html")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Ruta para restablecer la contraseña. Verifica el token y, si es válido, permite
    al usuario ingresar una nueva contraseña.

    Args:
        token (str): Token de restablecimiento de contraseña.

    Returns:
        str: HTML de la página para ingresar una nueva contraseña.
    """
    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=3600
        )
    except:
        flash("El enlace de recuperación es inválido o ha caducado.", "danger")
        return redirect(url_for("forgot"))
    if request.method == "POST":
        new_password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        mongo.db.users.update_one(
            {"email": email}, {"$set": {"password": hashed_password}}
        )
        flash("Tu contraseña ha sido restablecida exitosamente.")
        return redirect(url_for("login"))
    return render_template("auth/reset_password.html", token=token)


@app.route("/logout")
def logout():
    """
    Ruta para cerrar la sesión del usuario autenticado.

    Returns:
        str: Redirección a la página de login.
    """
    logout_user()
    flash("Logged out successfully. See you soon!", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
