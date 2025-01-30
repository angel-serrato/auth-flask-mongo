import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, logout_user, login_user, current_user
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo, MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
from flask_wtf.csrf import CSRFProtect
from bson import ObjectId
from pymongo.errors import ConnectionFailure

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

try:
    client = MongoClient(os.getenv('MONGO_URI'))
    client.admin.command('ping')
    print('Conexion exitosa a mongodb atlas')
except ConnectionFailure:
    print('Error de conexion')
except Exception as e:
    print(f'Error inesperado: {e}')

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data['_id'], user_data['username'])
        return None
    
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = mongo.db.users.find_one({'username': username})
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = User(user_data['_id'], user_data['username'])
            login_user(user)
            flash('Logged in successfully. Welcome back!', 'info')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password. Try again!', 'danger')
            return redirect(url_for('login'))
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if mongo.db.users.find_one({'username': username}):
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = {
            'username': username,
            'password': hashed_password,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        mongo.db.users.insert_one(user)
        # user_id = result.inserted_id
        flash('Account created successfully! Please log in.',  'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/admin')
@login_required
def admin():
    user_data = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
    if user_data:
        username = user_data['username']
        password_hash = user_data['password']
        created_at = user_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        return render_template('admin.html', username=username, password_hash=password_hash, created_at=created_at)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully. See you soon!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
