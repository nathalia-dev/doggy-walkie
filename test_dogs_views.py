import os
from unittest import TestCase

from models import db, connect_db, Dog_Owner, Dog_Walker, Dog, Message
from functions import is_worker

os.environ['DATABASE_URL'] = "postgresql:///doggy_walkie_test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all.
app.config['WTF_CSRF_ENABLED'] = False

class DogsTestCase(TestCase):
    """Test dogs views"""

    def setUp(self):
        """Create test client and sample data"""

        Dog_Owner.query.delete()
        Dog_Walker.query.delete()
        Message.query.delete()
        Dog.query.delete()

        self.client = app.test_client()

        self.testowner = Dog_Owner.signup(first_name = "Nathalia", last_name = "Owner", email = "nathalia@gmail.com", password = "123456")
        
        db.session.commit()

        self.testowner2 = Dog_Owner.signup(first_name = "Amanda", last_name = "Owner", email = "amanda@gmail.com", password = "123456")
        
        db.session.commit()

        self.testwalker = Dog_Walker.signup(first_name = "Jordana", last_name = "Walker", email = "jordana@gmail.com",  password = "123456")
        
        db.session.commit()

    def tearDown(self):

        db.session.rollback()
    
    def test_show_dog_profile_for_his_dog_owner(self):
        """ Will the page show dog details for his dog_owner? """
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog = Dog(dog_owner_id = self.testowner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)
            
            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()
        
            res = c.get(f"/dogs/{dog.id}")
            html = res.get_data(as_text = True)

            self.assertIn("Boby", html)
            self.assertIn("Akita", html)
            self.assertIn("4", html)
            self.assertIn("Edit", html)
            self.assertIn("Delete", html)
    
    def test_show_dog_profile_for_other_dog_owner(self):
        """ Will the page show dog details for another dog_owner? """
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner2.id
                sess["is_worker"] = is_worker(self.testowner2)
            
            other_user = Dog_Owner.query.filter_by(first_name = "Nathalia").first()
            dog = Dog(dog_owner_id = other_user.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)
            

            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()
        
            res = c.get(f"/dogs/{dog.id}", follow_redirects = True)
            html = res.get_data(as_text = True)

            
            self.assertIn("Access Unauthorized", html)
            self.assertNotIn("Boby", html)
    
    def test_show_dog_profile_for_dog_walker_with_previous_message(self):
        """ Will the page show dog details for a dog_walker who already exchange message with the dog_owner? """
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()
            dog = Dog(dog_owner_id = dog_owner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)
            message = Message(dog_owner_id = dog_owner.id, dog_walker_id = self.testwalker.id, text =  "Hiii")
            

            db.session.add_all([dog, message])
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()
        
            res = c.get(f"/dogs/{dog.id}", follow_redirects = True)
            html = res.get_data(as_text = True)
            
            self.assertIn("Boby", html)
            self.assertIn("Akita", html)
            self.assertIn("8", html)
            self.assertNotIn("Edit", html)
            self.assertNotIn("Delete", html)
    
    def test_show_dog_profile_for_dog_walker_with_no_message(self):
        """ Will the page show dog details for a dog_walker who did not exchange message with the dog_owner? """
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()
            dog = Dog(dog_owner_id = dog_owner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)
            

            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()
        
            res = c.get(f"/dogs/{dog.id}", follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertIn("Access Unauthorized", html)
            self.assertNotIn("Boby", html)

    def test_show_form_to_edit_dog_profile(self):
        """ Will the form to edit dog profile render correctly? """
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog = Dog(dog_owner_id = self.testowner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)
            

            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()
        
            res = c.get(f"/dogs/{dog.id}/edit")
            html = res.get_data(as_text = True)

            self.assertIn("Breed", html)
            self.assertIn("First Name", html)
            self.assertIn("Description", html)
            self.assertIn("Save", html)
    
    def test_show_form_to_edit_dog_profile_for_dog_walker_with_message(self):
        """ Will the form to edit a dog profile shows to a dog_walker that already exchange message with the dog_owner? """
        
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testwalker.id
                sess["is_worker"] = is_worker(self.testwalker)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()
            dog = Dog(dog_owner_id = dog_owner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)
            message = Message(dog_owner_id = dog_owner.id, dog_walker_id = self.testwalker.id, text =  "Hiii")
            

            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()
        
            res = c.get(f"/dogs/{dog.id}/edit", follow_redirects = True)
            html = res.get_data(as_text = True)

            self.assertNotIn("Breed", html)
            self.assertNotIn("First Name", html)
            self.assertNotIn("Description", html)
            self.assertIn("Access Unauthorized", html)
    
    def test_edit_dog_profile(self):
        """Will the the dog_owner be able to edit the dog profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog = Dog(dog_owner_id = self.testowner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)

            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()

            res = c.post(f"/dogs/{dog.id}/edit",data = {"first_name" : "Bobby", "breed" : "Lhasa Apso", "age" : 14} ,follow_redirects = True)
            html = res.get_data(as_text = True)


            dog = Dog.query.filter_by(first_name = "Bobby").first()

            self.assertEqual(dog.breed, "Lhasa Apso")
            self.assertIn("Bobby", html)
            self.assertIn("Lhasa Apso", html)
            self.assertIn("14", html)
            self.assertIn("Edit", html)
    
    def test_delete_dog_profile(self):
        """Will the the dog_owner be able to delete the dog profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog = Dog(dog_owner_id = self.testowner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)

            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()

            res = c.post(f"/dogs/{dog.id}/delete", follow_redirects = True)
            

            dog = Dog.query.filter_by(first_name = "Boby").first()

            self.assertIsNone(dog)
    
    def test_delete_dog_profile_another_user(self):
        """Will another dog_owner be able to delete the dog profile?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testowner2.id
                sess["is_worker"] = is_worker(self.testowner)
            
            dog_owner = Dog_Owner.query.filter_by(first_name = "Nathalia").first()
            dog = Dog(dog_owner_id = dog_owner.id, first_name = "Boby", breed = "Akita", weight = 8, age = 4)

            db.session.add(dog)
            db.session.commit()
            
            dog = Dog.query.filter_by(first_name = "Boby").first()

            res = c.post(f"/dogs/{dog.id}/delete", follow_redirects = True)
            html = res.get_data(as_text = True)
            

            dog = Dog.query.filter_by(first_name = "Boby").first()

            self.assertIsNotNone(dog)
            self.assertIn("Access Unauthorized", html)
            