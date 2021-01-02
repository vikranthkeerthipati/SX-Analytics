from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from slackTables.base import Base

class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True)
    _type = Column(String)
    block_id = Column(String)
    text = relationship("Text", uselist=True,back_populates="block")
    elements = relationship("Element", uselist=True, back_populates="block")
    accessory = relationship("Accessory", uselist=False, back_populates="block")
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message",back_populates="blocks")

class Accessory(Base):
    __tablename__ = "accessories"
    id = Column(Integer, primary_key=True)
    _type = Column(String)
    image_url = Column(String)
    alt_text = Column(String)
    action_id = Column(String)
    block_id = Column(Integer, ForeignKey("blocks.id"))
    block = relationship("Block", back_populates="accessory")

class AttachmentBlock(Block):
    __tablename__ = "attachment_blocks"
    __mapper_args__ = {'concrete':True}
    id = Column(Integer, primary_key=True)
    _type = Column(String)
    call_id = Column(String)
    call = relationship("Call", uselist=False, back_populates="attachment_block")
    block_id = Column(String)
    url = Column(String)
    api_decoration_available = Column(Boolean)
    attachment_id = Column(Integer, ForeignKey("attachments.id"))
    attachment = relationship("Attachment", back_populates="blocks")

class Call(Base):
    __tablename__ = "calls"
    id = Column(Integer, primary_key=True)
    call_id = Column(String)
    app_id = Column(String)
    app_icon_urls = relationship("AppIcon", uselist = False, back_populates="calls")
    date_start = Column(String)
    active_participants = Column(String)
    all_participants = Column(String)
    display_id = Column(String)
    join_url = Column(String)
    name = Column(String)
    created_by = Column(String)
    date_end = Column(String)
    channels = Column(String)
    is_dm_call = Column(Boolean)
    was_rejected = Column(Boolean)
    was_missed = Column(Boolean)
    was_accepted = Column(Boolean)
    has_ended = Column(Boolean)
    media_backend_type = Column(String)
    attachment_block_id = Column(Integer, ForeignKey("attachment_blocks.id"))
    attachment_block = relationship("AttachmentBlock", back_populates="call")
    

class AppIcon(Base):
    __tablename__ = "app_icons"
    id = Column(Integer, primary_key=True)
    image_32 = Column(String)
    image_36 = Column(String)
    image_48 = Column(String)
    image_64 = Column(String)
    image_72 = Column(String)
    image_96 = Column(String)
    image_128 = Column(String)
    image_192 = Column(String)
    image_512 = Column(String)
    image_1024 = Column(String)
    image_original = Column(String)
    call_id = Column(Integer, ForeignKey("calls.id"))
    calls = relationship("Call", back_populates="app_icon_urls")

class BotIcon(Base):
    __tablename__ = "bot_icons"
    id = Column(Integer, primary_key=True)
    image_36 = Column(String)
    image_48 = Column(String)
    image_64 = Column(String)
    image_72 = Column(String)
    bot_profile_id = Column(Integer, ForeignKey("bot_profiles.id"))
    bot_profile = relationship("BotProfile",back_populates="icons")

class MessageIcon(Base):
    __tablename__ = "message_icons"
    id = Column(Integer, primary_key=True)
    image_36 = Column(String)
    image_48 = Column(String)
    image_64 = Column(String)
    image_72 = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message",back_populates="icons")

class Element(Base):
    __tablename__ = "elements"
    id = Column(Integer, primary_key=True)
    _type = Column(String)
    text = relationship("Text", uselist=False, back_populates="element")
    action_id = Column(String)
    url = Column(String)
    image_url = Column(String)
    image_width = Column(Integer)
    image_height = Column(Integer)
    image_bytes = Column(Integer)
    alt_text = Column(String)
    value = Column(String)
    # style = relationship("Style", uselist=False, back_populates="element")
    style = Column(String)
    indent = Column(Integer)
    verbatim = Column(Boolean)
    offset = Column(Integer)
    subelements = relationship("Subelement", uselist=True, back_populates="element")
    block_id = Column(Integer, ForeignKey("blocks.id"))
    block = relationship("Block",back_populates="elements")    

class Subelement(Base):
    __tablename__ = "subelements"
    id = Column(Integer, primary_key=True)
    _type = Column(String)
    text =  relationship("Text", uselist=False, back_populates="subelement")
    style = relationship("Style", uselist=False, back_populates="subelement")
    user_id = Column(String)
    url = Column(String)
    name = Column(String)
    range = Column(String)
    channel_id = Column(String)
    skin_tone = Column(Integer)
    element_id = Column(Integer, ForeignKey("elements.id"))
    element = relationship("Element",back_populates="subelements")

class Style(Base):
    __tablename__ = "styles"
    id = Column(Integer, primary_key=True)
    bold = Column(Boolean)
    unlink = Column(Boolean)
    italic = Column(Boolean)
    code  = Column(Boolean)
    strike = Column(Boolean)
    # element_id = Column(Integer, ForeignKey("elements.id"))
    # element = relationship("Element", back_populates="style")
    subelement_id = Column(Integer, ForeignKey("subelements.id"))
    subelement = relationship("Subelement", back_populates="style")
    # action_id = Column(Integer, ForeignKey("actions.id"))
    # action = relationship("Action", back_populates="style")

class Text(Base):
    __tablename__ = "texts"
    id = Column(Integer, primary_key=True)
    _type = Column(String)
    text = Column(String)
    verbatim = Column(Boolean)    
    emoji = Column(Boolean)
    block_id = Column(Integer, ForeignKey("blocks.id"))
    block = relationship("Block", back_populates="text")   
    element_id = Column(Integer, ForeignKey("elements.id"))
    element = relationship("Element", back_populates="text")
    subelement_id = Column(Integer, ForeignKey("subelements.id"))
    subelement = relationship("Subelement", back_populates="text")
    action_id = Column(Integer, ForeignKey("actions.id"))
    action = relationship("Action",back_populates="text")
    


class BotProfile(Base):
    __tablename__ = "bot_profiles"
    id = Column(Integer, primary_key=True)
    bot_id = Column(String)
    deleted = Column(Boolean)
    name = Column(String)
    app_id = Column(String)
    icons = relationship("BotIcon", uselist=False, back_populates="bot_profile")
    team_id = Column(String)
    updated = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message",back_populates="bot_profile")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    avatar_hash = Column(String)
    image_72 = Column(String)
    first_name = Column(String)
    real_name = Column(String)
    display_name = Column(String)
    team = Column(String)
    name = Column(String)
    is_restricted = Column(Boolean)
    is_ultra_restricted = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message",back_populates="user_profile")

