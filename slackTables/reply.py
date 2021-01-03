from slackTables.message import Message
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
class Reply(Message):
    __tablename__ = "replies"
    id = Column(Integer, primary_key=True)
    root_client_msg_id = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message",back_populates="replies")
    __mapper_args__ = {
        'polymorphic_identity':'reply',
    } 