from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from profile import Profile
from slackTables.base import Base

class SlackUser(Base):
    __tablename__ = "slack_users"
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
    is_admin = Column(Boolean)
    is_owner = Column(Boolean)
    is_primary_owner = Column(Boolean)
    is_restricted = Column(Boolean)
    is_ultra_restricted = Column(Boolean)
    is_email_confirmed = Column(Boolean)
    is_bot = Column(Boolean)
    is_app_user = Column(Boolean)
    updated = Column(String)
    has_2fa = Column(Boolean)
    is_invited_user = Column(Boolean)
    is_workflow_bot = Column(Boolean)
