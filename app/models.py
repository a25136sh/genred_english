from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, DECIMAL, ForeignKey, BigInteger
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())


class Problem(Base):
    __tablename__ = "problems"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    genre_id = Column(Integer, ForeignKey("genres.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    answer_file_path = Column(String(1024), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())


class Result(Base):
    __tablename__ = "results"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    problem_id = Column(BigInteger, ForeignKey("problems.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    score = Column(DECIMAL(5, 2), nullable=False)
    try_file_path = Column(String(1024), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
