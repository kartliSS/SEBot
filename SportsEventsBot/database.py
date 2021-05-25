from aiogram import types
from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, Date)
from sqlalchemy import sql, ForeignKey

from config import DB_PASS, DB_USER, DB_NAME, DB_HOST

db = Gino()


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50))
    fullname = Column(String(50))
    user_id = Column(BigInteger)
    query: sql.Select


class Event(db.Model):
    __tablename__ = "events"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    type = Column(String(50))
    location = Column(String(50))
    date = Column(Date)
    query: sql.Select


class Check(db.Model):
    __tablename__ = "check"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    query: sql.Select


class DBCommands:

    async def get_user(self, user_id) -> User:
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def get_id(self, user):
        id = user.id
        return id

    async def add_new_user(self) -> User:
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.username = user.username
        new_user.full_name = user.full_name
        new_user.user_id = user.id
        await new_user.create()
        return new_user

    async def count_users(self) -> int:
        total = await db.func.count(User.id).gino.scalar()
        return total

    async def show_users(self) -> object:
        users = await User.query.gino.all()
        return users

    async def show_events(self):
        events = await Event.query.gino.all()
        return events

    async def show_check(self):
        check = await Check.query.gino.all()
        return check

    async def sub_event(self, id, event_id):
        new_check = Check()
        new_check.user_id = id
        new_check.event_id = event_id
        await new_check.create()
        return new_check

    async def unsub_event(self, user_id, event_id):
        await Check.delete.where(Check.user_id == user_id).where(Check.event_id == event_id).gino.status()
        return

    async def get_id(self, user_id):
        id = User().query.select(User.id).where(User.user_id == user_id).gino.first()
        return id

    async def show_my_events(self, event_id):
        events = await Event.query.where(Event.id == event_id).gino.first()
        return events

    async def show_ev_us(self, event_id):
        users = await User.query.where(User.id == Check.user_id).where(Check.event_id == event_id).gino.all()
        return users


async def create_db():
    await db.set_bind(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")
    await db.gino.create_all()
