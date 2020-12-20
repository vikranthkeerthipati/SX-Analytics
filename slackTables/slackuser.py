from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from profile import Profile
from slackTables.base import Base

class SlackUser(Base):
    __tablename__ = "slack_user"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    team_id = Column(String)
    name = Column(String)
    deleted = Column(Boolean)
    color = Column(String)
    real_name = Column(String)
    tz = Column(String)
    tz_label = Column(String)
    tz_offset = Column(Integer)
    profile = relationship("Profile", uselist=False, back_populates="slackuser")
    is_bot = Column(Boolean)
    is_app_user = Column(Boolean)
    updated = Column(Integer)
