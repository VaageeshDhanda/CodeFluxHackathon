from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Clear existing data to prevent conflicts
db.query(models.Rating).delete()
db.query(models.Payment).delete()
db.query(models.MarketplaceListing).delete()
db.query(models.DeliveryJob).delete()
db.query(models.Location).delete()
db.query(models.User).delete()
db.query(models.University).delete()
db.commit()

# 1. Create University
uni = models.University(id=1, name="Lovely Professional University")
db.add(uni)
db.commit()

# 2. Create Locations
loc1 = models.Location(id=1, name="Delivery Office 4", university_id=1)
loc2 = models.Location(id=2, name="Delivery Office 7", university_id=1)
loc3 = models.Location(id=3, name="Hostel 12", university_id=1)
loc4 = models.Location(id=4, name="Hostel 4", university_id=1)
db.add_all([loc1, loc2, loc3, loc4])
db.commit()

# 3. Create Admin User
admin_user = models.User(
    name="System Admin",
    email="admin@lpu.in",
    password="adminpassword123",
    university_id=1,
    is_admin=True
)
db.add(admin_user)

# 4. Create Student User
student_user = models.User(
    name="Rahul Sharma",
    email="rahul@lpu.in",
    password="studentpassword123",
    university_id=1,
    is_admin=False
)
db.add(student_user)
db.commit()

print("Database seeded successfully with university, locations, and admin/student accounts.")
db.close()