from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from slackTables.base import Base
from slackTables.attachment import Attachment
from slackTables.block import Block
from slackTables.reaction import Reaction
from slackTables.message import Message

class ChannelHistory(Base):
    __tablename__ = "channel_histories"
    id = Column(Integer, primary_key=True)
    channel_id = Column(String)
    messages = relationship("Message", uselist=True, back_populates="channel_history")
    

