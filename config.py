import os

class Config:
    SECRET_KEY = 'seducup-secret-2025'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///seducup.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False