import os
from unittest import TestCase

from models import db, Dog_Owner, Dog_Walker, Dog, Message, Appointment, Review

from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app

db.create_all()


class ReviewModelTestCase(TestCase):
    """Test model for reviews"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        walker1 = Dog_Walker.signup(
            first_name = "Jordana",
            last_name = "Walker",
            email="jordana@test.com",
            password="HASHED_PASSWORD",
        )

        owner1 = Dog_Owner.signup(
            first_name = "Nathalia",
            last_name = "Owner",
            email="nathalia@test.com",
            password="HASHED_PASSWORD",
        )

        db.session.commit()

        self.walker1_id = walker1.id
        self.owner1_id = owner1.id
        
        self.client = app.test_client()
    
    def tearDown(self):

        db.session.rollback()
    
    def test_review_model(self):
        """Testing review model"""

        appointment = Appointment(dog_owner_id = self.walker1_id, dog_walker_id = self.owner1_id, date = "2021-05-02", time_start = "03:00", day_period = "PM", duration = "15")
        
        db.session.add(appointment)
        db.session.commit()

        aptment = Appointment.query.filter_by(dog_owner_id = self.walker1_id).first()

        review = Review(appointment_id = aptment.id, rate = 5, comment = "Great")
        
        db.session.add(review)
        db.session.commit()

        r = Review.query.filter_by(appointment_id = aptment.id).first()

        self.assertEqual(r.rate, 5)
        self.assertEqual(r.comment, "Great")
        self.assertEqual(r.appointment.dog_walker.name, "Jordana Walker")
        self.assertEqual(r.appointment.dog_walker.name, "Nathalia Owner")