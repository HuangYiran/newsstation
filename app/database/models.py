from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Association table for articles and tags
article_tag = Table(
    'article_tag', 
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Source(Base):
    """Database model for news sources"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(50), unique=True, index=True)
    name = Column(String(100), index=True)
    url = Column(String(255))
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    language = Column(String(10), default="en")
    country = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    articles = relationship("Article", back_populates="source")

class Tag(Base):
    """Database model for article tags"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    articles = relationship("Article", secondary=article_tag, back_populates="tags")

class Article(Base):
    """Database model for news articles"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String(100), unique=True, index=True)
    title = Column(String(255), index=True)
    url = Column(String(255), unique=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, nullable=True)
    author_name = Column(String(100), nullable=True)
    author_url = Column(String(255), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    category = Column(String(50), index=True)
    image_url = Column(String(255), nullable=True)
    comments_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship("Source", back_populates="articles")
    tags = relationship("Tag", secondary=article_tag, back_populates="articles")

class User(Base):
    """Database model for users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100), nullable=True)
    github_id = Column(String(50), nullable=True, unique=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    bookmarks = relationship("Bookmark", back_populates="user")

class UserPreference(Base):
    """Database model for user preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    categories = Column(String(255), default="")  # Comma-separated list of categories
    sources = Column(String(255), default="")     # Comma-separated list of source IDs
    tags = Column(String(255), default="")        # Comma-separated list of tag names
    theme = Column(String(20), default="light")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

class Bookmark(Base):
    """Database model for bookmarked articles"""
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    article = relationship("Article") 