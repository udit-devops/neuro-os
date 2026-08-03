from app.models.users import User
from app.models.workspace import Workspace
from app.models.document import Document
from app.db.database import engine, Base

def init_db():
    Base.metadata.create_all(bind=engine)