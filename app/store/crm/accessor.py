import typing
from datetime import datetime, timedelta
from typing import Optional
import os
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret")
import bcrypt
import jwt
from sqlalchemy import select, func, update


from app.crm.model import Jokes, Topic, User, Rating

if typing.TYPE_CHECKING:
    from app.web.app import Application

class CrmAccessor:
    def __init__(self, app: "Application"):
        self.app = app

    async def add_topic(self, title: str) -> Topic:
        async with self.app.database.session() as session:
            async with session.begin():
                topic = Topic(title=title)
                session.add(topic)
            await session.commit()
        return topic

    async def add_joke(self, text: str, topic_id: int) -> Jokes:
        async with self.app.database.session() as session:
            async with session.begin():
                joke = Jokes(text=text, topic_id=topic_id)
                session.add(joke)

                result = await session.execute(select(Topic).where(Topic.topic_id == topic_id))
                topic =result.scalar_one_or_none()
                if topic:
                    topic.count +=1
            await session.commit()
        return joke

    async def list_topics(self) -> list[Topic]:
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.execute(select(Topic))
                topics = result.scalars().all()
                # result.scalars() - достает сами объекты из Topic из результата
                # иначе там будут просто строки запроса
                #.all() - превращает это в список Python
                for topic in topics:
                    count_result = await session.execute(
                        select(func.count(Jokes.joke_id))
                        .where(Jokes.topic_id == topic.topic_id)
                    )
                    topic.count = count_result.scalar()  # присваиваем актуальное значение
            return topics

    async def delete_joke(self, joke_id: int) -> bool:
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.execute(select(Jokes).where(Jokes.joke_id == joke_id))
                joke = result.scalar_one_or_none()
                if joke is None:
                    return False
                topic_id = joke.topic_id
                await session.delete(joke)

                if topic_id is not None:
                    topic = await session.get(Topic, topic_id)
                    if topic and topic.count > 0:
                        topic.count -= 1
        return True

    async def get_joke_by_title(self, text: str) -> list[Jokes]:
        async with self.app.database.session() as session:
            async with session.begin():
                query = select(Jokes)
                if text:
                    query = query.where(Jokes.text.ilike(f"%{text}%"))
                else:
                    query = select(Jokes)

                result = await session.execute(query)
                return result.scalars().all()



    async def register_user(self,name: str, mail: str, password:str, is_admin: bool = False) -> User:
        async with self.app.database.session() as session:
            async with session.begin():
                existing = await session.execute(select(User).where(User.mail == mail))
                if existing.scalar_one_or_none():
                    raise ValueError("User already exists")

                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                user = User(name = name, mail=mail, password=hashed_password.decode(), is_admin=is_admin)
                session.add(user)
                await session.flush()
                return user

    async def login_user(self, mail: str, password: str) -> User:
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.execute(select(User). where(User.mail == mail))
                user = result.scalar_one_or_none()

                if user is None:
                    raise ValueError("User not found")

                if not bcrypt.checkpw(password.encode(), user.password.encode()):
                    raise ValueError("Incorrect password")

                payload = {
                    "user_id": user.user_id,
                    "mail": user.mail,
                    "is_admin": user.is_admin,
                    "is_moderator": user.is_moderator,
                    "exp": datetime.utcnow() + timedelta(hours=1)
                }
                token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
                return token


    async def get_user(self) -> list[User]:
        async with self.app.database.session() as session:
            async with session.begin():
                user = await session.execute(select(User))

                return user.scalars().all()

    async def joke_update(self, joke_id: int, text: str ) -> Jokes:
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.execute(select(Jokes).where(Jokes.joke_id == joke_id))
                joke = result.scalar_one_or_none()
                if not joke:
                    return None
                joke.text = text
            await session.commit()
        return joke

    async def delete_topic(self, topic_id: int) -> bool:
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.execute(select(Topic).where(Topic.topic_id == topic_id))
                topic = result.scalar_one_or_none()
                if topic is None:
                    return False
                await session.delete(topic)
                return True

    async def rate_joke(self, joke_id : int, user_id: int, value: int) -> Jokes:
        async with self.app.database.session() as session:
            async with session.begin():
                result = await session.execute(select(Jokes).where(Jokes.joke_id == joke_id))
                joke = result.scalar_one_or_none()
                if not joke:
                    return None

                existing = await session.execute(select(Rating).where(Rating.joke_id == joke_id, Rating.user_id == user_id))
                rating = existing.scalar_one_or_none()
                if rating:
                    rating.value = value
                else:
                    rating = Rating(joke_id=joke_id, user_id=user_id, value=value)
                    session.add(rating)

            await session.refresh(rating)
            return rating
