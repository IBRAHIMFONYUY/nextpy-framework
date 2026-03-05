"""Database Guide - Blog Post"""

def get_template():
    return "blog/post.html"

async def get_server_side_props(context):
    return {
        "props": {
            "title": "Complete Database Guide for NextPy",
            "author": "NextPy Team",
            "date": "November 2025",
            "slug": "database-guide",
            "excerpt": "Master SQLAlchemy ORM with NextPy. SQLite, PostgreSQL, MySQL - all supported.",
            "content": """
# Complete Database Guide for NextPy

NextPy makes database integration simple with SQLAlchemy ORM. We'll cover everything from setup to advanced queries.

## Setup

Configure your database in `.env`:

```
DATABASE_URL=postgresql://user:pass@localhost/nextpy
```

Supported databases:
- SQLite (default): `sqlite:///./app.db`
- PostgreSQL: `postgresql://user:pass@host/db`
- MySQL: `mysql+pymysql://user:pass@host/db`

## Defining Models

Create models in `models/` directory:

```python
from nextpy.db import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    author = relationship("User", back_populates="posts")
```

## CRUD Operations

### Create

```python
from nextpy.db import get_session, User

session = get_session()
user = User(username="john", email="john@example.com", password="secret")
session.add(user)
session.commit()
session.close()
```

### Read

```python
session = get_session()

# Get all
users = session.query(User).all()

# Get by ID
user = session.query(User).filter_by(id=1).first()

# Filter
active_users = session.query(User).filter(User.username.contains("john")).all()

session.close()
```

### Update

```python
session = get_session()
user = session.query(User).filter_by(id=1).first()
user.email = "newemail@example.com"
session.commit()
session.close()
```

### Delete

```python
session = get_session()
user = session.query(User).filter_by(id=1).first()
session.delete(user)
session.commit()
session.close()
```

## Using in Pages

```python
from nextpy.db import get_session, User, Post

async def get_server_side_props(context):
    session = get_session()
    
    # Get posts with author
    posts = session.query(Post).join(User).all()
    
    # Convert to dict for template
    posts_data = []
    for post in posts:
        posts_data.append({
            "title": post.title,
            "content": post.content,
            "author": post.author.username,
            "created_at": post.created_at
        })
    
    session.close()
    
    return {"props": {"posts": posts_data}}
```

## Relationships

### One-to-Many

```python
class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")
```

### Many-to-Many

```python
from sqlalchemy import Table

student_course = Table(
    'student_course',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    courses = relationship("Course", secondary=student_course)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    students = relationship("Student", secondary=student_course)
```

## Performance Tips

1. **Use Sessions Properly**
   ```python
   session = get_session()
   try:
       # Your code
   finally:
       session.close()
   ```

2. **Cache Results**
   ```python
   from nextpy.utils.cache import cache_result
   
   @cache_result(ttl=3600)
   async def get_users():
       # This will be cached
   ```

3. **Use Pagination**
   ```python
   page = int(context.get("query", {}).get("page", 1))
   per_page = 20
   users = session.query(User).offset((page-1)*per_page).limit(per_page).all()
   ```

## Transactions

Handle transactions safely:

```python
session = get_session()
try:
    user = User(username="test")
    session.add(user)
    session.flush()  # Get the ID
    
    post = Post(title="Test", user_id=user.id)
    session.add(post)
    
    session.commit()
except Exception as e:
    session.rollback()
    raise e
finally:
    session.close()
```

## Migrations

Use Alembic for schema migrations:

```bash
pip install alembic
alembic init migrations
```

See the DOCUMENTATION.md for complete migration guide.

Happy querying! 🚀
"""
        }
    }
