from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.usuario import Base

engine = create_engine("sqlite:///fintrack.db")
Base.metadata.create_all(engine)

# scoped_session mantém a conversa com o banco "viva" durante toda a
# requisição, evitando erro de acessar dado depois da sessão fechada.
db_session = scoped_session(sessionmaker(bind=engine))