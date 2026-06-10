import json
from database import init_db, SessionLocal, Experience
from sentence_transformers import SentenceTransformer

# Load the real local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

MOCK_DATA = [
    {
      "experienceId": "01KQYJRFZSGB3XD5CJ1WP2RSAT",
      "userId": "01KNPFG0VRN6B6H6CHVSTA1ND8",
      "name": "Candlelight & Conversations sa",
      "shortDesc": "Romantic candlelight dinner event",
      "slug": "candlelight-&-conversations-sa",
      "status": "PUBLISHED",
      "address": "Dhanmondi 27",
      "city": "Dhaka",
      "state": "Dhaka",
      "country": "Bangladesh",
      "zipCode": "1209",
      "scheduleType": "ONTIME",
      "refundable": False,
      "detailsDesc": "Enjoy a beautiful candlelight dinner with your loved one.",
      "guestRequirements": "Couples only",
      "averageRating": 4.8,
      "reviewCount": 12,
      "categoryId": "01KN9HRHYQZMK44T6WR46FKXZ1",
      "isFeatured": True,
      "isActive": True,
      "price": 2000.0,
      "discount": 0.0,
      "discountType": "PERCENTAGE",
      "bookingCount": 5,
      "maxGuest": 2,
      "maxPerSlot": 2,
      "maxparticipants": 20
    }
]

def seed():
    print("Initializing Database...")
    init_db()
    
    db = SessionLocal()
    
    print("Generating real embeddings and inserting data...")
    for data in MOCK_DATA:
        exists = db.query(Experience).filter(Experience.experienceId == data["experienceId"]).first()
        if exists:
            print(f"Skipping {data['name']}, already exists.")
            continue
            
        # Create text to embed using important fields
        text_to_embed = f"Name: {data['name']}\nDescription: {data['shortDesc']} {data['detailsDesc']}\nCity: {data.get('city','')}\nPrice: {data['price']}"
        
        # Generate real vector (takes a bit of time first run)
        embedding = model.encode(text_to_embed).tolist()
        
        # Create DB record dynamically mapping JSON keys
        exp = Experience(**data, embedding=embedding)
        db.add(exp)
        
    db.commit()
    db.close()
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
