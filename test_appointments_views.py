import os
from unittest import TestCase

from models import db, connect_db, Dog_Owner, Dog_Walker, Appointment, Message
from functions import is_worker

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all.
app.config['WTF_CSRF_ENABLED'] = False

class AppointmentTestCase(TestCase):
    """Test appointment views"""

    def setUp(self):
        """Create test client and sample data"""

        Dog_Owner.query.delete()
        Dog_Walker.query.delete()
        Message.query.delete()
        Appointment.query.delete()


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
    
    def test_create_new_appointment_with_previous_message(self):
        """Will the dog_walker be able to create an appointment when he already exchange messages with the dog_owner?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
        dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()
        message = Message(dog_owner_id = dog_owner.id, dog_walker_id = self.testwalker.id, text = "Hi, good morning!")

        db.session.add(message)
        db.session.commit()

        res = c.post("appointments/new", data = {"dog_owner_id": dog_owner.id , "dog_walker_id": self.testwalker.id, "date": "02-03-2021", "time_start": "03:00", "day_period": "PM" , "duration":"15"} , follow_redirects = True)
        html = res.get_data(as_text = True)
        appointment = Appointment.query.filter_by(dog_walker_id = self.testwalker.id).first()

        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.duration, "15")
        self.assertIn("Nathalia Owner", html)
        self.assertIn("2021-02-03", html)
        self.assertIn("Done", html)
    
    def test_create_new_appointment_with_no_previous_message(self):
        """Will the dog_walker be able to create an appointment when he did not exchange messages with the dog_owner?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
        dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

        res = c.post("appointments/new", data = {"dog_owner_id": dog_owner.id , "dog_walker_id": self.testwalker.id, "date": "02-03-2021", "time_start": "03:00", "day_period": "PM" , "duration":"15"} , follow_redirects = True)
        html = res.get_data(as_text = True)
        appointment = Appointment.query.filter_by(dog_walker_id = self.testwalker.id).first()

        self.assertIsNone(appointment)
    
    def test_dog_owner_create_new_appointment(self):
        """Will the dog_owner be able to create an appointment?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
        dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()
        message = Message(dog_owner_id = self.testowner.id, dog_walker_id = dog_walker.id, text = "Hi, good morning!")

        db.session.add(message)
        db.session.commit()

        res = c.post("appointments/new", data = {"dog_owner_id": self.testowner.id , "dog_walker_id": dog_walker.id, "date": "02-03-2021", "time_start": "03:00", "day_period": "PM" , "duration":"15"} , follow_redirects = True)
        html = res.get_data(as_text = True)
        appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()

        self.assertIsNone(appointment)
        self.assertIn("Access Unauthorized", html)
    
    def test_change_appointment_status(self):
        """Will the dog_walker be able to change the appointment to done?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id , dog_walker_id = self.testwalker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15")
            
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = self.testwalker.id).first()

            res = c.post(f"appointments/{appointment.id}/change_status", data = {"status":True} , follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(appointment.status, True)
            self.assertNotIn("Nathalia Owner",html)
            self.assertNotIn("03:00",html)
    
    def test_change_appointment_status_to_not_done(self):
        """If the appointment status is already done. Will the dog_walker be able to change it to not done?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id , dog_walker_id = self.testwalker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15", status = True)
            
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = self.testwalker.id).first()

            res = c.post(f"appointments/{appointment.id}/change_status", data = {"status":False} , follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(appointment.status, True)
            self.assertNotIn("Nathalia Owner",html)
            self.assertNotIn("03:00",html)
    
    def test_dog_owner_change_appointment_status(self):
        """Will the dog_owner be able to change the appointment to done?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id , dog_walker_id = dog_walker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15")
            
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()

            res = c.post(f"appointments/{appointment.id}/change_status", data = {"status":True} , follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(appointment.status, False)
            self.assertIn("Access Unauthorized",html)

    def test_delete_appointment(self):
        """Will the dog_walker be able to delete an appointment?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id , dog_walker_id = self.testwalker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15")
            
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = self.testwalker.id).first()

            res = c.post(f"appointments/{appointment.id}/delete", follow_redirects = True)
            html = res.get_data(as_text = True)

            appointment = Appointment.query.filter_by(dog_walker_id = self.testwalker.id).first()

            self.assertIsNone(appointment)
            self.assertNotIn("Nathalia Owner",html)
            self.assertNotIn("03:00",html)

    
    def test_dog_owner_delete_appointment(self):
        """Will the dog_owner be able to delete the appointment?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id , dog_walker_id = dog_walker.id, date = "02-03-2021", time_start = "03:00", day_period = "PM" , duration = "15")
            
            db.session.add(appointment)
            db.session.commit()

            appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()

            res = c.post(f"appointments/{appointment.id}/delete", follow_redirects = True)
            html = res.get_data(as_text = True)

            appointment = Appointment.query.filter_by(dog_walker_id = dog_walker.id).first()

            self.assertIsNotNone(appointment)
        
            




            

    


    
