import os
from unittest import TestCase

from models import db, Dog_Owner, Dog_Walker, Dog, Message, Appointment, Review

from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for messages."""

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
    
    def test_message_model(self):
        """Testing message model"""

        dog_walker = Dog_Walker.query.get(self.walker1_id)
        dog_owner = Dog_Owner.query.get(self.owner1_id)

        message = Message(dog_owner_id = self.owner1_id, dog_walker_id = self.walker1_id, text = "Hi, how are you?")
        
        db.session.add(message)
        db.session.commit()

        msg = Message.query.filter_by(dog_owner_id = self.owner1_id).first()

        self.assertEqual(msg.dog_owner.name, "Nathalia Owner")
        self.assertEqual(msg.dog_walker.name, "Jordana Walker")
        self.assertEqual(msg.text, "Hi, how are you?")
        self.assertFalse(msg.is_sender_worker)
        self.assertIsNotNone(msg.date)


