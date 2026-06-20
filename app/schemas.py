from pydantic import Field,EmailStr,BaseModel


class Base(BaseModel):
    pass

class UserRegister(Base):
    
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
                          title="Password"
                          )
    
