from sqlalchemy import text

from app.models.users import User
from app.models.workspace import Workspace
from app.models.document import Document
from app.models.chunk import Chunk
from app.db.database import engine, Base

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)