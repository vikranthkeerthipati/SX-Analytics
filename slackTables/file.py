from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from slackTables.base import Base

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    file_id = Column(String)
    created= Column(Integer)
    timestamp= Column(Integer)
    name= Column(String)
    title= Column(String)
    mimetype= Column(String)
    filetype= Column(String)
    pretty_type= Column(String)
    user_id= Column(String)
    editable= Column(Boolean)
    size= Column(Integer)
    mode= Column(String)
    is_external= Column(Boolean)
    external_type= Column(String)
    is_public= Column(Boolean)
    public_url_shared= Column(Boolean)
    display_as_bot= Column(Boolean)
    username= Column(String)
    url_private= Column(String)
    url_private_download= Column(String)
    thumb_64= Column(String)
    thumb_80= Column(String)
    thumb_360= Column(String)
    thumb_360_w= Column(Integer)
    thumb_360_h= Column(Integer)
    thumb_480= Column(String)
    thumb_480_w= Column(Integer)
    thumb_480_h= Column(Integer)
    thumb_160= Column(String)
    thumb_720= Column(String)
    thumb_720_w= Column(Integer)
    thumb_720_h= Column(Integer)
    thumb_800= Column(String)
    thumb_800_w= Column(Integer)
    thumb_800_h= Column(Integer)
    thumb_960= Column(String)
    thumb_960_w= Column(Integer)
    thumb_960_h= Column(Integer)
    thumb_1024= Column(String)
    thumb_1024_w= Column(Integer)
    thumb_1024_h= Column(Integer)
    original_w= Column(Integer)
    original_h= Column(Integer)
    converted_pdf = Column(String)
    thumb_pdf = Column(String)
    thumb_pdf_w = Column(Integer)
    thumb_pdf_h = Column(Integer)
    thumb_video = Column(String)
    external_id = Column(String)
    external_url = Column(String)
    thumb_tiny= Column(String)
    permalink= Column(String)
    permalink_public= Column(String)
    is_starred= Column(Boolean)
    has_rich_preview= Column(Boolean)
    image_exif_rotation = Column(Integer)
    preview = Column(String)
    editor = Column(String)
    last_editor = Column(String)
    non_owner_editable = Column(Boolean)
    updated = Column(String)
    edit_link = Column(String)
    preview_highlight = Column(String)
    lines = Column(Integer)
    lines_more = Column(Integer)
    preview_is_truncated = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Message", back_populates="files")