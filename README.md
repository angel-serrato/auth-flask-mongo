# Auth Flask Mongo

A minimal user authentication web application built with Flask and MongoDB. It includes user registration, login, password reset (email), and basic template-based UI. This repository is intended as a small starter/example for learning how to wire Flask with MongoDB for authentication flows.

## Features

- User registration with email
- Login and logout
- Password reset via email (tokenized link)
- Simple Jinja2 templates for pages and emails

## Tech stack

- Python 3.8+
- Flask
- Flask extensions (used in the project: e.g., Flask-Mail — check code for exact imports)
- MongoDB (connection via URI in environment)

## Repository structure

- `app/` — Flask application package
	- `__init__.py` — app factory and configuration
	- `models.py` — User/data models and DB helpers
	- `config.py` — configuration classes
	- `templates/` — Jinja2 templates (views and email templates)
- `requirements.txt` — Python dependencies

## Quickstart (local)

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate  # on Windows (bash.exe)
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set environment variables

Create a `.env` file or export the variables in your shell. Common variables used by the app:

- `FLASK_APP=app` or the app entrypoint used by your project
- `FLASK_ENV=development` (optional)
- `SECRET_KEY` — a random secret for session and token signing
- `MONGO_URI` — connection string to your MongoDB instance (e.g., `mongodb://localhost:27017/auth-db`)
- Mail settings (if you want password reset emails to work):
	- `MAIL_SERVER`
	- `MAIL_PORT`
	- `MAIL_USERNAME`
	- `MAIL_PASSWORD`
	- `MAIL_USE_TLS` or `MAIL_USE_SSL`

Example (bash):

```bash
export FLASK_APP=app
export FLASK_ENV=development
export SECRET_KEY='replace-with-a-secure-random-value'
export MONGO_URI='mongodb://localhost:27017/auth-db'
# Mail settings for password reset emails (optional)
export MAIL_SERVER='smtp.example.com'
export MAIL_PORT=587
export MAIL_USERNAME='your@email'
export MAIL_PASSWORD='your-password'
export MAIL_USE_TLS=1
```

4. Run the app

```bash
flask run
```

Open http://127.0.0.1:5000/ in your browser.

## Usage

- Register a new user via the registration page.
- Login with the registered credentials.
- Use the "forgot password" flow to trigger a reset email (if mail is configured).

## Tests

This repository does not include a test suite by default. To add tests, consider using `pytest` and create tests for authentication flows, token creation/validation, and model/database helpers.

## Deployment notes

- Use a production-ready WSGI server such as Gunicorn or uWSGI.
- Configure a managed MongoDB instance or a secure self-hosted one.
- Ensure `SECRET_KEY` is kept secret in production.
- Configure a real SMTP provider or transactional email provider for password reset emails.

## Troubleshooting

- If you see database connection errors, verify `MONGO_URI` and that the MongoDB server is reachable.
- If email sending fails, verify mail settings and try a different SMTP provider or credentials.

## Contributing

Feel free to open issues or pull requests. Small improvements that are helpful:

- Add automated tests
- Add Dockerfile / docker-compose for local development
- Harden security (rate limiting, strong password hashing, CSRF protections)

## License

This project is provided as-is for learning purposes. Add a license file if you plan to redistribute.

---
If you want, I can also:

- add a short `dev` Docker Compose for local Mongo + Flask
- create a `.env.example` file with the environment variables
- add a minimal test using pytest to validate the registration/login flow

Tell me which of those you'd like and I'll implement it.