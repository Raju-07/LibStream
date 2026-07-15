from pydantic import Field, EmailStr, BaseModel, ConfigDict
from typing import Optional
import uuid
from datetime import datetime


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserRegister(Base):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(...,
                      description="Full Name",
                      max_length=50,
                      title="Full Name",
                      )
    
    username: str = Field(...,
                          max_length=100,
                          description="username",
                          title="username"
                          )
    
    email: EmailStr

    password: str = Field(...,
                          max_length=50,
                          description="Password",
                          title="Password",
                          )
    
class Books(Base):
    id: int = Field(...,description="Book id")
    name: str = Field(...,description="Book Name")
    author: str = Field(...,description="Author of the Book")
    category: Optional[str] = None
    location: Optional[str] = None

class UserResponse(Base):
    id: uuid.UUID
    name: str
    username: str
    email: str

class AddBookRequest(Base):
    name: str
    author: str
    category: str
    location: str
    is_assigned: bool = False

class UpdateBookRequest(Base):
    name: Optional[str] = Field(default="No Change, Remove this Column")
    author: Optional[str] = Field(default="No Change, Remove this Column")
    category: Optional[str] = Field(default="No Change, Remove this Column")
    location: Optional[str] = Field(default="No Change, Remove this Column")

class BookAssignRequest(Base):
    user_id: uuid.UUID
    book_id: int

class ViewBookResponse(Base):
    id: int
    name: str
    author: str
    category: str
    is_assigned: bool
    location: str


# schema for requesting the book
class BookRequest(Base):
    book_name : str = Field(...,max_length=100,description="Book Name")
    author: str = Field(default="Not Known",max_length=100,description="Book Description")
    edition: Optional[str]
    description: Optional[str]

# schema for Responsing the Requested book
class BookResponse(Base):
    id: int
    book_name: str
    author: str
    edition: str
    description: str
    status: Optional[str]