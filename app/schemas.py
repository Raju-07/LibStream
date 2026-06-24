from pydantic import Field,EmailStr,BaseModel,ConfigDict
from typing import Optional


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pass

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
    id: int
    name: str
    username: str
    email: str
