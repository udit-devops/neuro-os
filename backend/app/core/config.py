import os
import dotenv

dotenv.load_dotenv()
class Settings:
    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME")
        self.DEBUG = os.getenv("DEBUG") == "True"
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
