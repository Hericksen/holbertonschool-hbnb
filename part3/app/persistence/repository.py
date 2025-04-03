from abc import ABC, abstractmethod
<<<<<<< HEAD
from app import db
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import uuid
from datetime import datetime


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class BaseModel(db.Model):
    __abstract__ = True  # SQLAlchemy ne crée pas de table pour BaseModel

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

=======
>>>>>>> Hamza

class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    # Modification : on attend une instance
    @abstractmethod
    def update(self, instance):
        pass

    @abstractmethod
    def delete(self, instance):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}

    def add(self, obj):
        self._storage[obj.id] = obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        return next((obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value), None)
