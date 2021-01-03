from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from slackTables.base import Base

class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    reaction_users = relationship("ReactionUser", uselist=True, back_populates="reaction")
    count = Column(Integer)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message",back_populates="reactions")

class ReactionUser(Base):
    __tablename__ = "reaction_users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    reaction_id = Column(Integer, ForeignKey("reactions.id"))
    reaction = relationship("Reaction", back_populates="reaction_users")