from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from slackTables.base import Base
from slackTables.attachment import Attachment
from slackTables.block import Block
from slackTables.reaction import Reaction
from slackTables.file import File
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection



class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    client_msg_id = Column(String)
    _type = Column(String)
    subtype = Column(String)
    username = Column(String)
    text = Column(String)
    ts = Column(String)
    bot_id = Column(String)
    team = Column(String)
    edited = relationship("Edit", uselist=False, back_populates="message")
    attachments = relationship("Attachment", uselist=True, back_populates="message")
    blocks = relationship("Block", uselist=True, back_populates="message")
    reactions = relationship("Reaction", uselist=True, back_populates="message")
    files = relationship("File", uselist=True, back_populates="message")
    thread_ts = Column(String)
    reply_count = Column(Integer)
    reply_users_count = Column(Integer)
    latest_reply = Column(String)
    upload = Column(Boolean)
    reply_users = relationship("ReplyUser",uselist=True,back_populates="message")
    subscribed = Column(Boolean)
    last_read = Column(String)
    display_as_bot = Column(Boolean)
    # root = relationship("Root",uselist=False, back_populates="message")
    inviter = Column(String)
    pinned_to = Column(String)
    x_files = Column(String)
    old_name = Column(String)
    name = Column(String)
    purpose = Column(String)
    hidden = Column(Boolean)
    pinned_info = relationship("PinnedInfo",uselist=False,back_populates="message")
    bot_profile = relationship("BotProfile", uselist = False, back_populates="message")
    user_profile = relationship("UserProfile", uselist=False, back_populates="message")
    topic = Column(String)
    user_team = Column(String)
    source_team = Column(String)
    bot_link = Column(String)
    parent_user_id = Column(String)
    upload_reply_to = Column(String)
    replies = relationship("Reply", uselist=True, back_populates="message")
    icons = relationship("MessageIcon", uselist = False, back_populates="message")
    channel_history_id = Column(Integer, ForeignKey("channel_histories.id"))
    channel_history = relationship("ChannelHistory", back_populates="messages")
    __mapper_args__ = {
        'polymorphic_identity':'messages'
        # 'polymorphic_on':user_id
    }


class Edit(Base):
    __tablename__ = "edits"
    id = Column(Integer, primary_key=True)
    user = Column(String)
    ts = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message", back_populates="edited")  
class ReplyUser(Base):
    __tablename__ = "reply_users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message", back_populates="reply_users")

class PinnedInfo(Base):
    __tablename__ = "pinned_infos"
    id = Column(Integer, primary_key=True)
    channel = Column(String)
    pinned_by = Column(String)
    pinned_ts = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message", back_populates="pinned_info")

# class Root(Message):
#     __tablename__ = "root"
#     id = Column(Integer, primary_key=True)
#     message_id = Column(Integer, ForeignKey("messages.id"))
#     message = relationship("Message", back_populates="root")