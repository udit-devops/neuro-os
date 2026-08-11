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

        # AI providers (Groq = LLM; Ollama = local embeddings, no key needed)
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

        # CORS
        self.CORS_ORIGINS = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000",
            ).split(",")
            if origin.strip()
        ]

        # Auth (True = single-user local mode, no login/signup required)
        self.AUTH_DISABLED = os.getenv("AUTH_DISABLED") == "True"

        # Storage
        self.STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
        self.STORAGE_LOCAL_ROOT = os.getenv("STORAGE_LOCAL_ROOT", "storage")

        # Upload constraints
        self.MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25"))

        # Chunking
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

        # Embeddings (ollama | groq | gemini)
        self.EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")

        # LLM
        self.LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

        # Pipeline
        self.INGESTION_QUEUE = os.getenv("INGESTION_QUEUE", "neuroos:ingestion")
        self.EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))
        self.MAX_PROCESSING_ATTEMPTS = int(os.getenv("MAX_PROCESSING_ATTEMPTS", "3"))

settings = Settings()