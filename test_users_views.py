import os
import flask
from unittest import TestCase

from models import db, connect_db, Dog_Owner, Dog_Walker, Address, Dog, Message, Appointment, Review
from functions import is_worker

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all.
app.config['WTF_CSRF_ENABLED'] = False

class UsersTestCase(TestCase):
    """Test Both kind fo Users views"""

    def setUp(self):
        """Create test client and sample data"""

        Dog_Owner.query.delete()
        Dog_Walker.query.delete()
        Message.query.delete()
        Address.query.delete()
        Dog.query.delete()
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
    
    def test_search_dog_walkers(self):
        """Will the page render all the existing dog_walkers ? """

        with self.client as c:

            res = c.get("/dog_walkers")
            html= res.get_data(as_text = True)

            self.assertIn("Jordana Walker", html)
            self.assertIn("Joane Walker", html)
    
    def test_show_dog_owner_profile(self):
        """Will the page render the specific user details?"""
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            res = c.get(f"/dog_owners/{self.testowner.id}")
            html= res.get_data(as_text = True)

            self.assertIn("Nathalia Owner", html)
            self.assertIn("Dogs", html)

    def test_show_dog_owner_profile_no_login(self):
        """Will the page render the specific user details without user login?"""
        
        with self.client as c:

            res = c.get(f"/dog_owners/{self.testowner.id}",follow_redirects = True)
            html= res.get_data(as_text = True)

            self.assertNotIn("Nathalia Owner", html)
            self.assertIn("You need to login first", html)
    
    def test_show_dog_owner_profile_for_dog_walker_no_previous_message(self):
        """Will the page render the specific dog_owner details for a dog_walker with no previous messages?"""
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            res = c.get(f"/dog_owners/{dog_owner.id}",follow_redirects = True)
            html= res.get_data(as_text = True)

            self.assertNotIn("Nathalia Owner", html)
            self.assertIn("Access Unauthorized", html)
    
        
    def test_show_dog_owner_profile_for_dog_walker_with_message(self):
        """Will the page render the specific dog_owner details for a dog_walker with previous messages?"""
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            message = Message(dog_owner_id = dog_owner.id, dog_walker_id = self.testwalker.id, text = "Hi, how are you?")
            
            db.session.add(message)
            db.session.commit()

            res = c.get(f"/dog_owners/{dog_owner.id}",follow_redirects = True)
            html= res.get_data(as_text = True)

            self.assertIn("Nathalia Owner", html)
            self.assertNotIn("Address", html)
            self.assertNotIn("Edit", html)
            self.assertNotIn("Delete", html)
            self.assertIn("Dogs", html)

    def test_show_dog_owner_profile_for_another_dog_owner(self):
        """Will the page render the specific dog_owner details for another dog_owner?"""
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner2.id
                sess["is_worker"] = is_worker(self.testowner)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            res = c.get(f"/dog_owners/{dog_owner.id}",follow_redirects = True)
            html= res.get_data(as_text = True)

            self.assertNotIn("Nathalia Owner", html)
            self.assertIn("Access Unauthorized", html)
    
    def test_show_dog_walker_profile(self):
        """Will the page render the specific user details?"""
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)

            res = c.get(f"/dog_walkers/{self.testwalker.id}")
            html= res.get_data(as_text = True)

            self.assertIn("Jordana Walker", html)
            self.assertIn("Address", html)

    def test_show_dog_walker_profile_no_login(self):
        """Will the page render the specific user details without user login?"""
        
        with self.client as c:

            res = c.get(f"/dog_walkers/{self.testwalker.id}",follow_redirects = True)
            html= res.get_data(as_text = True)

            self.assertNotIn("Jordana Owner", html)
            self.assertIn("You need to login first", html)

    def test_show_dog_walker_profile_for_dog_owners(self):
        """Will the page render the specific user details for dog_owners?"""
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            dog_walker = Dog_Walker.query.filter_by(first_name  = "Jordana").first()

            res = c.get(f"/dog_walkers/{dog_walker.id}")
            html= res.get_data(as_text = True)

            self.assertIn("Jordana Walker", html)
            self.assertNotIn("Address", html)
            self.assertNotIn("Edit", html)
            self.assertNotIn("Delete", html)
            self.assertIn("Send a Message", html)

    def test_show_dog_walker_profile_for_another_dog_walker(self):
        """Will the page render the specific user details for another dog_walker?"""
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker2.id
                sess["is_worker"] = is_worker(self.testwalker2)

            dog_walker = Dog_Walker.query.filter_by(first_name  = "Jordana").first()

            res = c.get(f"/dog_walkers/{dog_walker.id}")
            html= res.get_data(as_text = True)

            self.assertNotIn("Send a Message", html)
            self.assertNotIn("Edit", html)
            self.assertNotIn("Address", html)
            self.assertNotIn("Delete", html)
            self.assertIn("Jordana Walker", html)

    def test_dog_owner_add_address(self):
        """Can the dog_owner add an address to his profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            res = c.post(f"/dog_owners/{self.testowner.id}/address", data = {"address" : "4337 Park Road", "zipcode" : 28209, "city" : "Charlotte", "state" : "North Carolina", "neighbor" : "Myers Park"}, follow_redirects = True)
            html = res.get_data(as_text = True)

            address = Address.query.filter_by(address = "4337 Park Road").first()

            self.assertIsNotNone(address)
            self.assertEqual(address.zipcode, 28209)
            self.assertIn("Nathalia", html)
            self.assertIn("Address saved", html)
            self.assertIn("Charlotte", html)
    
    def test_other_user_trying_to_add_address_to_dog_owner(self):
        """Can another person change or add address?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            res = c.post(f"/dog_owners/{dog_owner.id}/address", data = {"address" : "4337 Park Road", "zipcode" : 28209, "city" : "Charlotte", "state" : "North Carolina", "neighbor" : "Myers Park"}, follow_redirects = True)
            html = res.get_data(as_text = True)

            address = Address.query.filter_by(address = "4337 Park Road").first()

            self.assertIsNone(address)
            self.assertIn("Access Unauthorized", html)
            self.assertNotIn("Charlotte", html)
    
    def test_dog_walker_add_address(self):
        """Can the dog_walker add an address to his profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            res = c.post(f"/dog_walkers/{self.testwalker.id}/address", data = {"address" : "4337 Park Road", "zipcode" : 28209, "city" : "Charlotte", "state" : "North Carolina", "neighbor" : "Myers Park"}, follow_redirects = True)
            html = res.get_data(as_text = True)

            address = Address.query.filter_by(address = "4337 Park Road").first()

            self.assertIsNotNone(address)
            self.assertEqual(address.zipcode, 28209)
            self.assertIn("Jordana", html)
            self.assertIn("Address saved", html)
            self.assertIn("Charlotte", html)
    
    def test_other_user_trying_to_add_address_to_dog_walker(self):
        """Can another person change or add address?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            res = c.post(f"/dog_walkers/{dog_walker.id}/address", data = {"address" : "4337 Park Road", "zipcode" : 28209, "city" : "Charlotte", "state" : "North Carolina", "neighbor" : "Myers Park"}, follow_redirects = True)
            html = res.get_data(as_text = True)

            address = Address.query.filter_by(address = "4337 Park Road").first()

            self.assertIsNone(address)
            self.assertIn("Access Unauthorized", html)
            self.assertNotIn("Charlotte", html)
    
    def show_address_form_page(self):
        """Does the address form page renders correctly?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            res = c.get(f"/dog_walkers/{dog_walker.id}/address")
            html = res.get_data(as_text = True)

            self.assertIn("Zipcode", html)
            self.assertIn("Address", html)
            self.assertIn("Neighbor", html)
            self.assertIn("Save", html)

    def test_dog_owner_edit_profile(self):
        """Can the dog_owner edit his profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            res = c.post(f"/dog_owners/profile", data = {"last_name" : "New Last Name", "password" : 123456}, follow_redirects = True)
            html = res.get_data(as_text = True)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            self.assertEqual(dog_owner.first_name, "Nathalia")
            self.assertEqual(dog_owner.last_name, "New Last Name")
            self.assertIn("Nathalia", html)

    def test_dog_owner_edit_profile_incorrect_password(self):
        """Can the dog_owner edit his profile with incorrect password?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            res = c.post(f"/dog_owners/profile", data = {"last_name" : "New Last Name", "password" : 111111}, follow_redirects = True)
            html = res.get_data(as_text = True)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            self.assertNotEqual(dog_owner.last_name, "New Last Name")
            self.assertIn("Incorrect password - Impossible to edit profile.", html)
    
    def test_dog_walker_edit_profile(self):
        """Can the dog_walker edit his profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            res = c.post(f"/dog_walkers/profile", data = {"last_name" : "New Last Name", "password" : 123456}, follow_redirects = True)
            html = res.get_data(as_text = True)

            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            self.assertEqual(dog_walker.first_name, "Jordana")
            self.assertEqual(dog_walker.last_name, "New Last Name")
            self.assertIn("Jordana", html)

    def test_dog_walker_edit_profile_incorrect_password(self):
        """Can the dog_walker edit his profile with incorrect password?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            res = c.post(f"/dog_walkers/profile", data = {"last_name" : "New Last Name", "password" : 111111}, follow_redirects = True)
            html = res.get_data(as_text = True)

            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            self.assertNotEqual(dog_walker.last_name, "New Last Name")
            self.assertIn("Incorrect password - Impossible to edit profile.", html)

    def show_edit_profile_form(self):
        """Does the edit profile form render correctly?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            res = c.get(f"/dog_walkers/profile")
            html = res.get_data(as_text = True)

            self.assertIn("Password")
            self.assertIn("Description")
            self.assertIn("First Name")
            self.assertIn("Last Name")

    def test_dog_owner_delete(self):
        """Can dog_owner delete his profile succesfully?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            res = c.post(f"/dog_owners/delete", follow_redirects = True)
            html = res.get_data(as_text = True)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            self.assertIsNone(dog_owner)
            self.assertIn("The user was deleted", html)
            self.assertIn("WELCOME", html)

    def test_dog_walker_delete(self):
        """Can dog_walker delete his profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testwalker.id
                    sess["is_worker"] = is_worker(self.testwalker)
                
            res = c.post(f"/dog_walkers/delete", follow_redirects = True)
            html = res.get_data(as_text = True)

            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            self.assertIsNone(dog_walker)
            self.assertIn("The user was deleted", html)
            self.assertIn("WELCOME", html)

    def test_show_dog_owner_messages(self):
        """Will the page show all the users that dog_owner is exchanging messages?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            testwalker = Dog_Walker.query.filter_by(first_name = "Jordana").first()
            testwalker2 = Dog_Walker.query.filter_by(first_name = "Joane").first()

            message1 = Message(dog_owner_id = self.testowner.id, dog_walker_id = testwalker.id, text = "Hi, how are you?")
            message2 = Message(dog_owner_id = self.testowner.id, dog_walker_id = testwalker2.id, text = "Hi, can we talk")

            db.session.add_all([message1,message2])
            db.session.commit()

            res = c.get(f"/dog_owners/{self.testowner.id}/messages")
            html = res.get_data(as_text = True)

            self.assertIn("MESSAGES", html)
            self.assertIn("Joane Walker", html)
            self.assertIn("Jordana Walker", html)
            self.assertNotIn("Hi, how are you?", html)
    
    def test_show_dog_walker_messages(self):
        """Will the page show all the users that dog_walker is exchanging messages?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            testowner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()
            testowner2 = Dog_Owner.query.filter_by(first_name = "Amanda").first()

            message1 = Message(dog_owner_id = testowner.id, dog_walker_id = self.testwalker.id , text = "Hi, how are you?")
            message2 = Message(dog_owner_id = testowner2.id, dog_walker_id = self.testwalker.id , text = "Hi, can we talk")

            db.session.add_all([message1,message2])
            db.session.commit()

            res = c.get(f"/dog_walkers/{self.testwalker.id}/messages")
            html = res.get_data(as_text = True)

            self.assertIn("MESSAGES", html)
            self.assertIn("Amanda Owner", html)
            self.assertIn("Nathalia Owner", html)
            self.assertNotIn("Hi, how are you?", html)

    def test_show_dog_owner_appointments(self):
        """ Will the page show all the dog_owner appointments? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id, dog_walker_id = dog_walker.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15")

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_owners/{self.testowner.id}/appointments")
            html = res.get_data(as_text = True)

            self.assertIn("APPOINTMENTS", html)
            self.assertIn("Jordana Walker", html)
            self.assertIn("02-20-2021", html)
            self.assertIn("15", html)
    
    def test_show_dog_owner_appointments_for_another_user(self):
        """ Will the page show all the dog_owner appointments for another user? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()
            other_user = Dog_Owner.query.filter_by(first_name = "Amanda").first()

            appointment = Appointment(dog_owner_id = other_user.id, dog_walker_id = dog_walker.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15")

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_owners/{other_user.id}/appointments", follow_redirects  = True)
            html = res.get_data(as_text = True)

            self.assertNotIn("APPOINTMENTS", html)
            self.assertNotIn("Jordana Walker", html)
            self.assertNotIn("02-20-2021", html)
            self.assertIn("Access Unauthorized", html)

    def test_show_dog_owner_done_appointments(self):
        """ Will the page show all the dog_owner done appointments? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()

            appointment = Appointment(dog_owner_id = self.testowner.id, dog_walker_id = dog_walker.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15", status = True)

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_owners/{self.testowner.id}/done_appointments")
            html = res.get_data(as_text = True)

            self.assertIn("DONE APPOINTMENTS", html)
            self.assertIn("Jordana Walker", html)
            self.assertIn("02-20-2021", html)
            self.assertIn("Rate", html)
    
    def test_show_dog_owner_done_appointments_for_another_user(self):
        """ Will the page show all the dog_owner done appointments for another user? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            dog_walker = Dog_Walker.query.filter_by(first_name = "Jordana").first()
            other_user = Dog_Owner.query.filter_by(first_name = "Amanda").first()

            appointment = Appointment(dog_owner_id = other_user.id, dog_walker_id = dog_walker.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15", status = True)

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_owners/{other_user.id}/done_appointments", follow_redirects  = True)
            html = res.get_data(as_text = True)

            self.assertNotIn("Rate", html)
            self.assertNotIn("Jordana Walker", html)
            self.assertNotIn("02-20-2021", html)
            self.assertIn("Access Unauthorized", html)

    def test_show_dog_walker_appointments(self):
        """ Will the page show all the dog_walker appointments? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id, dog_walker_id = self.testwalker.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15")

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_walkers/{self.testwalker.id}/appointments")
            html = res.get_data(as_text = True)

            self.assertIn("APPOINTMENTS", html)
            self.assertIn("Nathalia Owner", html)
            self.assertIn("02-20-2021", html)
            self.assertIn("15", html)
            self.assertIn("Done", html)
    
    def test_show_dog_walker_appointments_for_another_user(self):
        """ Will the page show all the dog_walker appointments for another user? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)

            other_user = Dog_Walker.query.filter_by(first_name = "Joane").first()
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id, dog_walker_id = other_user.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15")

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_walkers/{other_user.id}/appointments", follow_redirects  = True)
            html = res.get_data(as_text = True)

            self.assertNotIn("APPOINTMENTS", html)
            self.assertNotIn("Nathalia Owner", html)
            self.assertNotIn("02-20-2021", html)
            self.assertNotIn("Done", html)
            self.assertIn("Access Unauthorized", html)

    def test_show_dog_walker_done_appointments(self):
        """ Will the page show all the dog_walker done appointments? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)

            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id, dog_walker_id = self.testwalker.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15", status = True)

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_walkers/{self.testwalker.id}/done_appointments")
            html = res.get_data(as_text = True)

            self.assertIn("DONE APPOINTMENTS", html)
            self.assertIn("Nathalia Owner", html)
            self.assertIn("02-20-2021", html)

    
    def test_show_dog_walker_done_appointments_for_another_user(self):
        """ Will the page show all the dog_walker done appointments for another user? """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)

            other_user = Dog_Walker.query.filter_by(first_name = "Joane").first()
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            appointment = Appointment(dog_owner_id = dog_owner.id, dog_walker_id = other_user.id, date = "02-20-2021", time_start = "03:00", day_period = "PM", duration = "15", status = True)

            db.session.add(appointment)
            db.session.commit()

            res = c.get(f"/dog_walkers/{other_user.id}/done_appointments", follow_redirects  = True)
            html = res.get_data(as_text = True)

            self.assertNotIn("DONE APPOINTMENTS", html)
            self.assertNotIn("Nathalia Owner", html)
            self.assertNotIn("02-20-2021", html)
            self.assertIn("Access Unauthorized", html)

    def test_show_dog_owner_dogs(self):
        """Will the page render all the dogs for an specific dog_owner?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog = Dog(dog_owner_id = self.testowner.id, first_name = "Boby", breed = "Poodle", weight = 8, age = 4)
        
            db.session.add(dog)
            db.session.commit()

            res = c.get(f"/dog_owners/{self.testowner.id}/dogs")
            html = res.get_data(as_text = True)

            self.assertIn("BOBY", html)
            self.assertIn("Poodle", html)
    
    def test_show_dog_owner_dogs_for_dog_walker_with_message(self):
        """Will the page show for a dog_walker the dog_owner's dog, if they already exchange messages?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            dog = Dog(dog_owner_id = dog_owner.id, first_name = "Boby", breed = "Poodle", weight = 8, age = 4)
            message = Message(dog_owner_id = dog_owner.id, dog_walker_id = self.testwalker.id, text = "Hiii")
            
            db.session.add_all([dog, message])
            db.session.commit()

            res = c.get(f"/dog_owners/{dog_owner.id}/dogs")
            html = res.get_data(as_text = True)

            self.assertIn("BOBY", html)
            self.assertIn("Poodle", html)
    
    def test_show_dog_owner_dogs_for_dog_walker_with_no_message(self):
        """Will the page show for a dog_walker the dog_owner's dog, if they did not exchange messages?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()

            dog = Dog(dog_owner_id = dog_owner.id, first_name = "Boby", breed = "Poodle", weight = 8, age = 4)
            
            db.session.add(dog)
            db.session.commit()

            res = c.get(f"/dog_owners/{dog_owner.id}/dogs", follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertNotIn("BOBY", html)
            self.assertNotIn("Poodle", html)
            self.assertIn("Access Unauthorized", html)

    def test_add_dogs_form (self):
        """Will the page render correctly the form to add a dog?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
        
            res = c.get(f"/dog_owners/{self.testowner.id}/dogs/add")
            html = res.get_data(as_text = True)

            self.assertEqual(200, res.status_code)
            self.assertIn("First Name", html)
            self.assertIn("Breed", html)
            self.assertIn("Poodle", html)
            self.assertIn("Lhasa Apso", html)
            self.assertIn("Save", html)
    
    def test_add_dogs_in_dog_owner_profile(self):
        """Will dog_owner be able to add a dog?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)


            res = c.post(f"/dog_owners/{self.testowner.id}/dogs/add", data = {"dog_owner_id": self.testowner.id, "first_name": "boby", "breed": "Lhasa Apso", "weight": 12, "age":2}, follow_redirects = True)
            html = res.get_data(as_text = True)

            dog = Dog.query.filter_by(first_name = "boby").first()

            self.assertEqual(dog.breed, "Lhasa Apso")
            self.assertEqual(dog.dog_owner.name, "Nathalia Owner")

            #dog.description comes directly by the external api. So it is working, also. 
            self.assertIsNotNone(dog.description)

            self.assertIn("Dog added", html)
            self.assertIn("BOBY", html)
            self.assertIn("LHASA APSO", html)

        
    def test_add_dogs_in_dog_owner_profile_logged_as_another_user(self):
        """Will dog_owner be able to add a dog for another dog_owner?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            other_user= Dog_Owner.query.filter_by(first_name = "Amanda").first()

            res = c.post(f"/dog_owners/{other_user.id}/dogs/add", data = {"dog_owner_id": other_user.id, "first_name": "boby", "breed": "Lhasa Apso", "weight": 12, "age":2}, follow_redirects = True)
            html = res.get_data(as_text = True)

            dog = Dog.query.filter_by(first_name = "boby").first()

            self.assertIsNone(dog)
            self.assertNotIn("Dog added", html)
            self.assertNotIn("BOBY", html)
            self.assertIn("Access Unauthorized", html)

##################################################
# Homepage, Login, Logout, SignUp tests

    def test_homepage_no_login(self):
        """Will the homepage render correctly ?"""
        with self.client as c:
            res = c.get("/")
            html = res.get_data(as_text = True)

            self.assertIn("Ready for a walk?", html)
            self.assertIn("Sign up", html)
            self.assertIn("New to Doggy Walkie?", html)
    
    def test_homepage_with_login(self):
        """Will the homepage render correctly ?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            res = c.get("/", follow_redirects = True)
            html = res.get_data(as_text = True)

            
            self.assertNotIn("Ready for a walk?", html)
            self.assertNotIn("New to Doggy Walkie?", html)
            self.assertIn("Nathalia Owner", html)
            self.assertIn("Edit", html)
            self.assertIn("Delete", html)

    def test_login_page(self):
        """Will the login form render correctly ?"""

        with self.client as c:
            res = c.get("/login")
            html = res.get_data(as_text = True)

            self.assertIn("E-mail", html)
            self.assertIn("Password", html)
            self.assertIn("Are you a Dog Walker?", html)
            self.assertIn("Log in", html)

    def test_dog_owner_login(self):
        """Will dog_owner be able to login ?"""

        with self.client as c:

            res = c.post("/login", data = {"email":"nathalia@gmail.com", "password":"123456"}, follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertIn("Nathalia Owner", html)
            self.assertIn("Dogs", html)
            self.assertIsNotNone(flask.session[CURR_USER_KEY])
            self.assertFalse(flask.session["is_worker"])

    def test_dog_walker_login(self):
        """Will dog_owner be able to login ?"""

        with self.client as c:

            res = c.post("/login", data = {"email":"jordana@gmail.com", "password":"123456", "dog_walker_check": True}, follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertIn("Jordana Walker", html)
            self.assertNotIn("Dogs", html)
            self.assertIsNotNone(flask.session[CURR_USER_KEY])
            self.assertTrue(flask.session["is_worker"])

    def test_signup_page(self):
        """Will the sign up form render correctly ?"""

        with self.client as c:
            res = c.get("/signup")
            html = res.get_data(as_text = True)

            self.assertIn("First Name", html)
            self.assertIn("Last Name", html)
            self.assertIn("E-mail", html)
            self.assertIn("Password", html)
            self.assertIn("Are you a Dog Walker?", html)
            self.assertIn("Signup", html)

    def test_dog_owner_signup(self):
        """Will dog_owner be able to signup ?"""

        with self.client as c:

            res = c.post("/signup", data = {"first_name": "Ed", "last_name": "Owner" , "email":"ed@gmail.com", "password":"123456"}, follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertIn("Ed Owner", html)
            self.assertIn("Dogs", html)
            self.assertIsNotNone(flask.session[CURR_USER_KEY])
            self.assertFalse(flask.session["is_worker"])
    
    def test_dog_walker_signup(self):
        """Will dog_owner be able to signup ?"""

        with self.client as c:

            res = c.post("/signup", data = {"first_name": "Maya", "last_name": "Walker", "email":"maya@gmail.com", "password":"123456", "dog_walker_check": True}, follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertIn("Maya Walker", html)
            self.assertNotIn("Dogs", html)
            self.assertIsNotNone(flask.session[CURR_USER_KEY])
            self.assertTrue(flask.session["is_worker"])


    def test_logout(self): 
        """Will the logout work correctly?"""
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)

            res = c.get("/logout", follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertEqual(len(flask.session), 0)
            self.assertIn("Ready for a walk?", html)




           
    

           






        
    
    

            

