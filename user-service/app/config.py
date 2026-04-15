# DB URL, JWT secret, env vars
import os

class Config:
    SECRET_KEY = "super-secret-key"  
    SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False