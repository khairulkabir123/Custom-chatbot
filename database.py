import os
from sqlalchemy import create_engine, Column, String, Float, Text, text, Boolean, Integer, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@127.0.0.1:15432/outings_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Experience(Base):
    __tablename__ = "experiences"

    experienceId = Column(String, primary_key=True, index=True)
    userId = Column(String, index=True, nullable=True)
    name = Column(String, index=True)
    shortDesc = Column(Text, nullable=True)
    slug = Column(String, nullable=True)
    status = Column(String, nullable=True)
    
    address = Column(String, nullable=True)
    city = Column(String, index=True, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    zipCode = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    scheduleType = Column(String, nullable=True)
    cancelPolicy = Column(Text, nullable=True)
    latePolicy = Column(Text, nullable=True)
    reschedulePolicy = Column(Text, nullable=True)
    refundable = Column(Boolean, default=False)
    coverImage = Column(String, nullable=True)
    cancellationFee = Column(Float, nullable=True)
    
    detailsDesc = Column(Text, nullable=True)
    includes = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    guestRequirements = Column(Text, nullable=True)
    agreement = Column(Text, nullable=True)
    
    averageRating = Column(Float, default=0)
    reviewCount = Column(Integer, default=0)
    categoryId = Column(String, nullable=True)
    
    createdAt = Column(String, nullable=True)
    updatedAt = Column(String, nullable=True)
    deletedAt = Column(String, nullable=True)
    
    activities = Column(JSON, nullable=True)
    timeslots = Column(JSON, nullable=True)
    
    startDate = Column(String, nullable=True)
    endDate = Column(String, nullable=True)
    startTime = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    endTime = Column(String, nullable=True)
    
    isFeatured = Column(Boolean, default=False)
    isActive = Column(Boolean, default=True)
    
    price = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    discountType = Column(String, nullable=True)
    openWindowDays = Column(Integer, nullable=True)
    bookingCount = Column(Integer, default=0)
    maxGuest = Column(Integer, nullable=True)
    maxPerSlot = Column(Integer, nullable=True)
    maxparticipants = Column(Integer, nullable=True)
    
    # 384 is the dimension for the 'all-MiniLM-L6-v2' sentence-transformer model
    embedding = Column(Vector(384))

def init_db():
    # Create the pgvector extension if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
