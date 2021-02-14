import os
from unittest import TestCase

from models import db, Dog_Owner, Dog_Walker, Dog, Message, Appointment, Review

from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app

db.create_all()


class DogModelTestCase(TestCase):
    """Test model for dog."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        owner1 = Dog_Owner.signup(
            first_name = "Nathalia",
            last_name = "Owner",
            email="nathalia@test.com",
            password="HASHED_PASSWORD",
        )

        db.session.commit()


        self.owner1_id = owner1.id

        self.client = app.test_client()
    
    def tearDown(self):
        db.session.rollback()
    
    def test_dog_model(self):
        """Does basic model work?"""
        
        dog = Dog(dog_owner_id = self.owner1_id, first_name = "dog_test", breed = "breed_test", weight = 8,  age = 4)
        db.session.add(dog)
        db.session.commit()

        d = Dog.query.filter_by(dog_owner_id = self.owner1_id).first()

        # User should have the email,username and password provided in line 48.
        self.assertEqual(d.first_name, "dog_test")
        self.assertEqual(d.breed, "breed_test")
        self.assertEqual(d.dog_owner.name, "Nathalia Owner")
        self.assertIsNotNone(d.photo)