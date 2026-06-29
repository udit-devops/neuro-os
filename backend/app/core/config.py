import os
import dotenv

dotenv.load_dotenv()
class Settings:
    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME")
        self.DEBUG = os.getenv("DEBUG") == "True"

settings = Settings()
