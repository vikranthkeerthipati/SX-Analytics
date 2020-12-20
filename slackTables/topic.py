from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from slackTables.base import Base
from slackTables.slackuser import SlackUser


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key = True)
    value = Column(String)
    creator_id = Column(String)
    last_set = Column(Integer)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    channel = relationship("Channel",back_populates="topic")