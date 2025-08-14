from contextlib import contextmanager
from sqlalchemy import create_engine, text, Row
from sqlalchemy.orm import sessionmaker,declarative_base,Session,DeclarativeMeta
from typing import Generator,Any, Dict, List

from core.config import config_manager

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        connection_string = (config_manager.settings.database.url)
        pool_size = (config_manager.settings.database.pool_size)
        echo_sql = (config_manager.settings.database.echo_sql)

        self.engine = create_engine(connection_string, pool_size=pool_size, echo=echo_sql, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        self._initialized = True

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def execute(self, sql_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self.get_session() as db:
            statement = text(sql_query)
            result = db.execute(statement, params)
            return result.mappings().all()

    def scalar(self, sql_query: str, params: Dict[str, Any] = None) -> Any:
        with self.get_session() as db:
            statement = text(sql_query)
            result = db.execute(statement, params)
            return result.scalar_one_or_none()

    def commit(self, sql_query: str, params: Dict[str, Any] = None) -> int:
        with self.get_session() as db:
            statement = text(sql_query)
            result = db.execute(statement, params)
            db.commit()
            return result.rowcount

db_manager = DatabaseManager()

Base = declarative_base()

class ModelMeta(DeclarativeMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        
        if not hasattr(cls, 'to_dict'):
            def to_dict(self):
                return {col.name: getattr(self, col.name) for col in self.__table__.columns}
            cls.to_dict = to_dict

class ModelBase(Base, metaclass=ModelMeta):
    __abstract__ = True