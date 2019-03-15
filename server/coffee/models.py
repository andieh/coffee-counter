import time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
	__tablename__ = "User"
	id = Column(String(16), primary_key=True)
	username = Column(String(120))
	joined = Column(Integer, index=True, default=time.time())
	events = relationship('Event')

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Event(Base):
	__tablename__ = "Event"
	e_id = Column(Integer, primary_key=True)
	what = Column(Integer)
	timestamp = Column(Integer, index=True, default=time.time())
	user_id = Column(String(16), ForeignKey('User.id'))

	User = relationship("User", primaryjoin="Event.user_id == User.id")

	def __repr__(self):
		return '<Event {} from User {}>'.format(self.what, self.user_id)