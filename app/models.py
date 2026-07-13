from sqlalchemy import Integer,String,Date,UUID,DateTime,func,ForeignKey,Boolean,cast,extract
from sqlalchemy.orm import mapped_column,Mapped,DeclarativeBase,relationship,column_property
import uuid
from datetime import datetime,timezone,timedelta
from app.db.session import engine

class Base(DeclarativeBase):
    pass

class UserModal(Base):
    __tablename__= "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID,nullable=False,default= lambda: uuid.uuid4(),primary_key=True,index=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False)
    username: Mapped[str] = mapped_column(String(70),nullable=False,unique=True)
    email: Mapped[str] = mapped_column(String(100),unique=True,index=True,nullable=False)
    password: Mapped[str] = mapped_column(String,nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),server_default=func.current_timestamp())
    
    assignments: Mapped[list["BookAssignModal"]] = relationship(
        back_populates="user",
        cascade= "all,delete-orphan"
        )
    
    class config:
        from_attributes = True


class BooksModal(Base):

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True,nullable=False,autoincrement=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False)
    author: Mapped[str] = mapped_column(String(100),nullable=False)
    category: Mapped[str] = mapped_column(String(100),nullable=False,default='General')
    location: Mapped[str] = mapped_column(String(50),nullable=False)
    is_assigned: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                server_default=func.current_timestamp(),
                                default=datetime.now(timezone.utc))

    assignments: Mapped[list["BookAssignModal"]] = relationship(back_populates='book',
                                                    cascade='all,delete-orphan')
    

    class config:
        from_attributes = True

class BookAssignModal(Base):

    __tablename__ = "book_assign"

    index: Mapped[int] = mapped_column(Integer,autoincrement=True,
                                       primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'),
                                               nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'),nullable=False)
    expired_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True),
                    default=datetime.now(timezone.utc)+timedelta(days=10),
                    server_default= func.current_timestamp() + timedelta(days=10))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.current_timestamp())
    is_return: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
    
    # days_left : Mapped[int] = column_property(
        # cast(extract('epoch',expired_at - func.current_timestamp)/86400 ,Integer))
    
    user: Mapped["UserModal"] = relationship(back_populates='assignments')
    book: Mapped["BooksModal"] = relationship(back_populates='assignments')
    
    class config:
        from_attributes = True

