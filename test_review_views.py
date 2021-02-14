import os
from unittest import TestCase

from models import db, connect_db, Dog_Owner, Dog_Walker, Appointment, Message, Review
from functions import is_worker

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all.
app.config['WTF_CSRF_ENABLED'] = False

class ReviewTestCase(TestCase):
    """Test review views"""

    def setUp(self):
        """Create test client and sample data"""

        Dog_Owner.query.delete()
        Dog_Walker.query.delete()
        Message.query.delete()
        Appointment.query.delete()
        Review.query.delete()


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

    def test_dog_owner_review_appointment(self):
        """Will the dog_owner be able to review the done_appointment?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id , dog_walker_id = dog_walker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15", status = True)
            
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()

            res = c.post(f"/review/{appointment.id}", data = {"appointment_id": appointment.id, "rate": 4}, follow_redirects = True)
            html = res.get_data(as_text = True)

            review = Review.query.filter_by(rate = 4).first()
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            self.assertIsNotNone(review)
            self.assertEqual(review.rate, 4)
            self.assertEqual(dog_walker.rate, 4)
            self.assertIn("Rated: 4", html)
    
    def test_dog_owner_review_appointment_twice(self):
        """Will the dog_owner be able to review the done_appointment two times?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id , dog_walker_id = dog_walker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15", status = True)
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()
            review = Review(appointment_id = appointment.id, rate = 4)

            db.session.add(review)
            db.session.commit()

            res = c.post(f"/review/{appointment.id}", data = {"appointment_id": appointment.id, "rate": 3}, follow_redirects = True)
            html = res.get_data(as_text = True)

            old_review = Review.query.filter_by(rate = 4).first()
            new_review = Review.query.filter_by(rate = 3).first()
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            self.assertIsNone(new_review)
            self.assertEqual(old_review.rate, 4)

    def test_dog_owner_review_appointment_not_done(self):
        """Will the dog_owner be able to review the appointment that is not done?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id , dog_walker_id = dog_walker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15")
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()

            res = c.post(f"/review/{appointment.id}", data = {"appointment_id": appointment.id, "rate": 3}, follow_redirects = True)
            html = res.get_data(as_text = True)

            review = Review.query.filter_by(rate = 3).first()
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            self.assertIsNone(review)
            self.assertIsNone(dog_walker.rate)
            self.assertIn("Access Unauthorized", html)

    def test_dog_walker_review_appointment(self):
        """Will the dog_walker be able to review his done_appointment?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id , dog_walker_id = self.testwalker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15", status = True)
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = self.testwalker.id).first()

            res = c.post(f"/review/{appointment.id}", data = {"appointment_id": appointment.id, "rate": 5}, follow_redirects = True)
            html = res.get_data(as_text = True)

            
            review = Review.query.filter_by(rate = 5).first()
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            self.assertIsNone(review)
            self.assertIsNone(dog_walker.rate, 4)
            self.assertIn("Access Unauthorized", html)
    
    def test_dog_owner_review_appointment_form(self):
        """Will the page render the correct form to review the appointment?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id , dog_walker_id = dog_walker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15", status = True)
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()

            res = c.get(f"/review/{appointment.id}", follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertIn("JORDANA WALKER", html)
            self.assertIn("Save", html)


            
    
