import os
import dotenv

dotenv.load_dotenv()
class Settings:
    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME")
        self.DEBUG = os.getenv("DEBUG") == "True"
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SECRET_KEY = os.getenv("SECRET_KEY")

settings = Settings()
