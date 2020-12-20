from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from profile import Profile
from slackTables.base import Base
from slackTables.slackuser import SlackUser

class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key = True)
    channel_id = Column(String)
    name = Column(String)
    is_channel = Column(Boolean)
    is_group = Column(Boolean)
    is_im = Column(Boolean)
    created = Column(Integer)
    is_archived = Column(Boolean)
    is_general = Column(Boolean)
    unlinked = Column(Integer)
    name_normalized = Column(String)
    is_shared = Column(Boolean)
    frozen_reason = Column(String)
    parent_conversation = Column(String)
    creator_id = Column(String)
    is_ext_shared = Column(Boolean)
    is_org_shared = Column(Boolean)
    shared_team_ids = relationship("SharedTeamId", uselist=True, back_populates="channel")
    pending_shared = relationship("PendingShared",uselist=True, back_populates="channel")
    pending_connected_team_ids = relationship("PendingConnectedTeamId", uselist=True, back_populates="channel")
    is_pending_ext_shared = Column(Boolean)
    is_member = Column(Boolean)
    is_private = Column(Boolean)
    is_mpim = Column(Boolean)
    topic = relationship("Topic", uselist=False, back_populates="channel")
    purpose = relationship("Purpose", uselist=False, back_populates="channel")
    previous_names = relationship("PreviousName", uselist=True, back_populates="channel")
    num_members = Column(Integer)

class SharedTeamId(Base):
    __tablename__ = "shared_team_ids"
    id = Column(Integer, primary_key = True)
    team_id = Column(String)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    channel = relationship("Channel",back_populates="shared_team_ids")
class PendingShared(Base):
    __tablename__ = "pending_shared"
    id = Column(Integer, primary_key=True)
    pending_id = Column(String)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    channel = relationship("Channel",back_populates="pending_shared")
class PendingConnectedTeamId(Base):
    __tablename__ = "pending_connected_team_ids"
    id = Column(Integer, primary_key=True)
    pending_connected_team_id = Column(String)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    channel = relationship("Channel",back_populates="pending_connected_team_ids")
class PreviousName(Base):
    __tablename__ = "previous_names"
    id = Column(Integer, primary_key=True)
    previous_name = Column(String)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    channel = relationship("Channel",back_populates="previous_names")