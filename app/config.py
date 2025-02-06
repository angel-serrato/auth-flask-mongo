import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_SENDER = os.getenv("SENDGRID_SENDER")
