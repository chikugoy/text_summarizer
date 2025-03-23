import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Image(Base):
    """画像モデル"""
    __tablename__ = "images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary_id = Column(UUID(as_uuid=True), ForeignKey("summaries.id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    ocr_text = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # リレーションシップ
    summary = relationship("Summary", back_populates="images")
    
    def __repr__(self):
        return f"<Image(id={self.id}, file_name='{self.file_name}', page_number={self.page_number})>"
