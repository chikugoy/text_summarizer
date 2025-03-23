import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Summary(Base):
    """要約モデル"""
    __tablename__ = "summaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    original_text = Column(Text, nullable=False)
    summarized_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # リレーションシップ
    images = relationship("Image", back_populates="summary", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Summary(id={self.id}, title='{self.title}')>"
