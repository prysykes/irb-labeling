# config.py
import json

with open("config.json") as fp:
    config = json.load(fp)

class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get("MAIL_USERNAME") 
    MAIL_PASSWORD = config.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = config.get("MAIL_DEFAULT_SENDER")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF protection in testing