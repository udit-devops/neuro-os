

class workspace(Base):
    __tablename__ = "workspace"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    