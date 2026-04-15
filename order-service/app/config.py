class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///orders.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USER_SERVICE_URL = "http://user-service:5001"