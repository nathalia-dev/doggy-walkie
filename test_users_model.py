import os
from unittest import TestCase

from models import db, Dog_Owner, Dog_Walker, Dog, Message, Appointment, Review, Address

from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test models for all users."""

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
    
    def test_dog_walker_model(self):
        """Does basic model work?"""
        u = Dog_Walker.query.get(self.walker1_id)

        
        self.assertEqual(u.name, "Jordana Walker")
        self.assertEqual(u.email, "jordana@test.com")
        self.assertIn("$2b$12", u.password)
    
    def test_dog_owner_model(self):
        """Does basic model work?"""
        u = Dog_Owner.query.get(self.owner1_id)

        
        self.assertEqual(u.name, "Nathalia Owner")
        self.assertEqual(u.email, "nathalia@test.com")
        self.assertIn("$2b$12", u.password)
    
    def test_dog_walker_authenticate(self):
        """Testing the authenticate method for dog_walker"""

        u = Dog_Walker.query.get(self.walker1_id)
        true_result = Dog_Walker.authenticate(u.email, "HASHED_PASSWORD")
        false_result = Dog_Walker.authenticate(u.email, "HASD_PASSWORD")

        self.assertTrue(true_result)
        self.assertFalse(false_result)

            
    def test_dog_owner_authenticate(self):
        """Testing the authenticate method for dog_owner"""

        u = Dog_Owner.query.get(self.owner1_id)
        true_result = Dog_Owner.authenticate(u.email, "HASHED_PASSWORD")
        false_result = Dog_Owner.authenticate(u.email, "HASD_PASSWORD")

        self.assertTrue(true_result)
        self.assertFalse(false_result)
    
    def test_dog_walker_invalid_email(self):
        """Testing invalid email: trying to create an user with the same email used for another dog_owner"""

        walker2 = Dog_Walker.signup(
            first_name = "Joane",
            last_name = "Walker",
            email="jordana@test.com",
            password="HASHED_PASSWORD",
        )

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()


    def test_dog_owner_invalid_email(self):
        """Testing invalid email: trying to create an user without an email"""

        owner2 = Dog_Owner.signup(
            first_name = "Amanda",
            last_name = "Owner",
            email=None,
            password="HASHED_PASSWORD",
        )

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()


    def test_dog_walker_update_address(self):
        """Testing dog_walker update address function"""

        address = Address(address = "202 Main Street", zipcode = 123456, city = "New York", state = "NY", neighbor = "Manhattan")
        
        db.session.add(address)
        db.session.commit()

        Dog_Walker.update_address("jordana@test.com", "202 Main Street")

        dog_walker = Dog_Walker.query.get(self.walker1_id)

        self.assertEqual(dog_walker.address.zipcode, 123456)
        self.assertEqual(dog_walker.address.neighbor, "Manhattan")
    
    def test_dog_owner_update_address(self):
        """Testing dog_owner update address function"""

        address = Address(address = "202 Main Street", zipcode = 123456, city = "New York", state = "NY", neighbor = "Manhattan")
        
        db.session.add(address)
        db.session.commit()

        Dog_Owner.update_address("nathalia@test.com", "202 Main Street")

        dog_owner = Dog_Owner.query.get(self.owner1_id)

        self.assertEqual(dog_owner.address.zipcode, 123456)
        self.assertEqual(dog_owner.address.neighbor, "Manhattan")