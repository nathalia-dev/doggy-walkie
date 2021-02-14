import os
from unittest import TestCase

from models import db, connect_db, Dog_Owner, Dog_Walker, Message
from functions import is_worker

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all.
app.config['WTF_CSRF_ENABLED'] = False

class MessageTestCase(TestCase):
    """Test messages views"""

    def setUp(self):
        """Create test client and sample data"""

        Dog_Owner.query.delete()
        Dog_Walker.query.delete()
        Message.query.delete()


        self.client = app.test_client()

        self.testowner = Dog_Owner.signup(first_name = "Nathalia", last_name = "Owner", email = "nathalia@gmail.com", password = "123456")
        
        db.session.commit()

        self.testowner2 = Dog_Owner.signup(first_name = "Amanda", last_name = "Owner", email = "amanda@gmail.com", password = "123456")
        
        db.session.commit()

        self.testwalker = Dog_Walker.signup(first_name = "Jordana", last_name = "Walker", email = "jordana@gmail.com",  password = "123456")
        
        db.session.commit()

        self.testwalker2 = Dog_Walker.signup(first_name = "Joane", last_name = "Walker", email = "joane@gmail.com",  password = "123456")

        db.session.commit()

    def tearDown(self):

        db.session.rollback()

    def test_show_messages_between_two_users(self):
        """Show the messages between two users and render the form to send a new one"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
        dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

        message = Message(dog_owner_id = self.testowner.id, dog_walker_id = dog_walker.id, text = "Hi, good morning!")

        db.session.add(message)
        db.session.commit()

        res = c.get(f"/messages/{self.testowner.id}/{dog_walker.id}")
        html = res.get_data(as_text = True)

        self.assertIn("Nathalia Owner", html)
        self.assertIn("Jordana Walker", html)
        self.assertIn("Hi, good morning!", html)
        self.assertIn("Send", html)
    
    def test_show_messages_between_two_users_for_third_user(self):
        """Will the app show the messages between two users for a third different one?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
        dog_owner = Dog_Owner.query.filter_by(first_name = "Amanda").first()
        dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

        message = Message(dog_owner_id = dog_owner.id, dog_walker_id = dog_walker.id, text = "Hi, good morning!")

        db.session.add(message)
        db.session.commit()

        res = c.get(f"/messages/{dog_owner.id}/{dog_walker.id}", follow_redirects = True)
        html = res.get_data(as_text = True)

        self.assertIn("Access Unauthorized", html)
        self.assertNotIn("Jordana Walker", html)
        self.assertNotIn("Hi, good morning!", html)
        self.assertNotIn("Amanda Owner", html)
    
    def test_send_message(self):
        """Testing the feature to send a message to one specific user"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
        dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

        res = c.post(f"/messages/{self.testowner.id}/{dog_walker.id}", data = {"text": "Hi, good afternoon!"}, follow_redirects = True)
        html = res.get_data(as_text = True)

        message = Message.query.filter_by(text = "Hi, good afternoon!").first()    

        self.assertIsNotNone(message)
        self.assertEqual(message.text, "Hi, good afternoon!")
        self.assertIn("Nathalia Owner", html)
        self.assertIn("Jordana Walker", html)
        self.assertIn("Hi, good afternoon!", html)
        self.assertIn("Send", html)
    
    def test_dog_walker_send_the_first_message(self):
        """Can the dog_walker be the one who send a message?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
        dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

        res = c.post(f"/messages/{dog_owner.id}/{self.testwalker.id}", data = {"text": "Hi, good afternoon!"}, follow_redirects = True)
        html = res.get_data(as_text = True)

        message = Message.query.filter_by(text = "Hi, good afternoon!").first()    

        self.assertIsNone(message)
        self.assertIn("Access Unauthorized", html)
        self.assertNotIn("Nathalia Owner", html)
        self.assertNotIn("Hi, good afternoon!", html)
        self.assertNotIn("Send", html)


               


