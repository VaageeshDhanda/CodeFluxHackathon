@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        uni = db.query(models.University).filter_by(id=1).first()
        if not uni:
            uni = models.University(id=1, name="Lovely Professional University")
            db.add(uni)
            db.commit()

        loc = db.query(models.Location).filter_by(id=1).first()
        if not loc:
            locs = [
                models.Location(id=1, name="Delivery Office 4", university_id=1),
                models.Location(id=2, name="Delivery Office 7", university_id=1),
                models.Location(id=3, name="Hostel 12", university_id=1),
                models.Location(id=4, name="Hostel 4", university_id=1)
            ]
            db.add_all(locs)
            db.commit()

        admin = db.query(models.User).filter_by(email="admin@lpu.in").first()
        if not admin:
            admin_user = models.User(
                name="System Admin",
                email="admin@lpu.in",
                password="adminpassword123",
                university_id=1,
                is_admin=True
            )
            student_user = models.User(
                name="Rahul Sharma",
                email="rahul@lpu.in",
                password="studentpassword123",
                university_id=1,
                is_admin=False
            )
            db.add_all([admin_user, student_user])
            db.commit()

        # Seed sample delivery job and marketplace listing if empty
        if db.query(models.DeliveryJob).count() == 0:
            student = db.query(models.User).filter_by(email="rahul@lpu.in").first()
            student_id = student.id if student else 2
            
            sample_job = models.DeliveryJob(
                title="Cafeteria Snack Run",
                description="Deliver food court items to Hostel 12",
                pickup_location_id=1,
                dropoff_location_id=3,
                reward=50.0,
                user_id=student_id,
                status="pending"
            )
            sample_listing = models.MarketplaceListing(
                title="Calculus Textbook",
                description="Barely used engineering math book",
                price=300.0,
                category="Books",
                user_id=student_id,
                status="available"
            )
            db.add_all([sample_job, sample_listing])
            db.commit()
    finally:
        db.close()