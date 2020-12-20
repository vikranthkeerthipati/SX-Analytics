from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from slackTables.base import Base

class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    phone = Column(String)
    skype = Column(String)
    real_name = Column(String)
    real_name_normalized = Column(String)
    display_name = Column(String)
    display_name_normalized = Column(String)
    status_text = Column(String)
    status_emoji = Column(String)
    status_expiration = Column(Integer)
    avatar_hash = Column(String)
    always_active = Column(Boolean)
    first_name = Column(String)
    last_name = Column(String)
    image_24 = Column(String)
    image_32 = Column(String)
    image_48 = Column(String)
    image_72 = Column(String)
    image_192 = Column(String)
    image_512 = Column(String)
    status_text_canonical = Column(String)
    team = Column(String)
    slackuser_id = Column(Integer, ForeignKey("slack_user.id"))
    slackuser = relationship("SlackUser",back_populates="profile")

