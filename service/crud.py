from typing import Type, TypeVar, Generic, List, Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.param_functions import Depends
from config.db.connection import get_db
from sqlalchemy.exc import NoResultFound,SQLAlchemyError


# Generic types
ModelType = TypeVar("ModelType")  # SQLAlchemy model type
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  # Pydantic schema for creating
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)  # Pydantic schema for responses

class CRUDService(Generic[ModelType, CreateSchemaType, ResponseSchemaType]):
    def __init__(
        self,
        db: Session = Depends(get_db),
        model: Type[ModelType] = None,
        response_schema: Type[ResponseSchemaType] = None,
    ):
        self.db = db
        self.model = model
        self.response_schema = response_schema

    # Get all records
    def get_all(self) -> List[ResponseSchemaType]:
        records = self.db.query(self.model).all()
        return [self.response_schema.model_validate(record) for record in records]

    # Get a record by ID
    def get_by_id(self, id: int) -> ResponseSchemaType:
        record = self.db.query(self.model).filter(self.model.id == id).first()
        if not record:
            raise NoResultFound(f"{self.model.__name__} with id {id} not found")  
        return self.response_schema.model_validate(record)

    # Create a record
    def create(self, obj_in: CreateSchemaType) -> ResponseSchemaType:
        obj = self.model(**obj_in.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self.response_schema.model_validate(obj)

    # Delete a record
    def delete(self, id: int) -> str:
        record = self.db.query(self.model).filter(self.model.id == id).first()
        if not record:
            raise NoResultFound(f"{self.model.__name__} with id {id} not found")
        self.db.delete(record)
        self.db.commit()
        return f"{self.model.__name__} with id {id} deleted"

    # Update a record
    def update(self, id: int, obj_in: CreateSchemaType) -> ResponseSchemaType:
        record = self.db.query(self.model).filter(self.model.id == id).first()
        if not record:
            raise NoResultFound(f"{self.model.__name__} with id {id} not found")
        try:
            for key, value in obj_in.model_dump().items():
                setattr(record, key, value)
            self.db.commit()
            self.db.refresh(record)
            return self.response_schema.model_validate(record)
        except SQLAlchemyError as e:
            raise e