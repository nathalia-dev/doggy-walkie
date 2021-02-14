import os
from unittest import TestCase

from models import db, Dog_Owner, Dog_Walker, Address

from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app

db.create_all()


class AddressModelTestCase(TestCase):
    """Test models for address."""

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
    
    def test_address_model(self):
        """Testing address model"""

        address = Address(address = "202 Main Street", zipcode = 123456, city = "New York", state = "NY", neighbor = "Manhattan")
        
        db.session.add(address)
        db.session.commit()

        ad = Address.query.filter_by(zipcode = 123456).first()

        self.assertEqual(ad.zipcode, 123456)
        self.assertEqual(ad.state, "NY")
        self.assertEqual(ad.neighbor, "Manhattan")