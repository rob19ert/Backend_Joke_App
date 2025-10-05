from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, Mapped
from sqlalchemy.testing.schema import mapped_column

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable = False)
    mail = Column(String(50), unique=True, nullable = False)
    password = Column(String(255), nullable = False)
    # один пользователь может иметь много анекдотов
    jokes = relationship('Jokes', back_populates='author')
    ratings = relationship('Rating', back_populates='user')

    is_admin = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)


class Topic(Base):
    __tablename__ = 'topics'

    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column (String(150), unique = True, nullable = False)
    count =  Column(Integer, default=0)

    # один топик может содержать много анекдотов
    jokes = relationship('Jokes', back_populates='topic')

class Jokes(Base):
    __tablename__ = 'jokes'
    joke_id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable = False)

    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='CASCADE'))
    author_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'))

    topic = relationship('Topic', back_populates='jokes')
    author = relationship('User', back_populates='jokes')
    ratings = relationship('Rating', back_populates='jokes', cascade="all, delete-orphan")


class Rating(Base):
    __tablename__ = 'ratings'

    rating_id = Column(Integer, primary_key=True, autoincrement=True)
    joke_id = Column(Integer, ForeignKey('jokes.joke_id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    value = Column(Integer, default=0)

    jokes = relationship('Jokes', back_populates='ratings')
    user = relationship('User', back_populates='ratings')


