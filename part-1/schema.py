from database import Base, engine
from sqlalchemy import Column, String, Integer

# NTUOSS Member Schema
class DBMember(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    school = Column(String)
    graduation_year = Column(Integer)

Base.metadata.create_all(bind=engine)