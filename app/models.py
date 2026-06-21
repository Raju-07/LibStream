from sqlalchemy import Integer,String,Date,UUID,DateTime,func
from sqlalchemy.orm import mapped_column,Mapped,DeclarativeBase
import uuid
from datetime import datetime,timezone

class Base(DeclarativeBase):
    pass

class UserModal(Base):
    __tablename__= "users"

    uuid: Mapped[UUID] = mapped_column(UUID,nullable=False,default= lambda: uuid.uuid4(),primary_key=True,index=True)
    name: Mapped[String] = mapped_column(String(50),nullable=False)
    email: Mapped[String] = mapped_column(String(100),unique=True,index=True,nullable=False)
    password: Mapped[str] = mapped_column(String,nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),server_default=func.current_timestamp())


class BooksModal(Base):

    __tablename__ = "books"

    id: Mapped[Integer] = mapped_column(Integer,primary_key=True,index=True,nullable=False,autoincrement=True)
    name: Mapped[String] = mapped_column(String(50),nullable=False)
    author: Mapped[String] = mapped_column(String(100))
    total: Mapped[Integer] = mapped_column(Integer,nullable=False)
    assign: Mapped[Integer] = mapped_column(Integer,nullable=False,default=0)
    added_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.current_timestamp(),default=datetime.now(timezone.utc))
    category: Mapped[String] = mapped_column(String(100),nullable=False,default='General')
    location: Mapped[String] = mapped_column(String(50),nullable=False)

class BookAssignModal(Base):

    __tablename__ = "book_assign"

    index: Mapped[Integer] = mapped_column(Integer,autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(UUID)
    