from app import app
from models import db, Dog_Owner, Dog_Walker, Address, Dog, Message, Appointment


db.drop_all()
db.create_all()

address1 = Address(address = "112 Poplar Street", zipcode = 28202, city = "Charlotte", state = "North Carolina", neighbor = "Dilworth")
address2 = Address(address = "4337 Kenilworth Avenue", zipcode = 28204, city = "Charlotte", state = "North Carolina", neighbor = "Uptown")
address3 = Address(address = "202 Park Road", zipcode = 28209, city = "Charlotte", state = "North Carolina", neighbor = "Myers Park")
address4 = Address(address = "905 S Sharon Amity", zipcode = 28211, city = "Charlotte", state = "North Carolina", neighbor = "Cotwolds")

Dog_Owner.signup(first_name = "kate", last_name = "Owner", email = "kate@email.com", password = "123456")
Dog_Owner.signup(first_name = "kevin", last_name = "Owner", email = "kevin@email.com", password = "123456")

Dog_Walker.signup(first_name = "Randon", last_name = "Walker", email = "randon@email.com",  password = "123456")
Dog_Walker.signup(first_name = "Beth", last_name = "Walker", email = "beth@email.com",  password = "123456")
Dog_Walker.signup(first_name = "Rebecca", last_name = "Walker", email = "rebecca@email.com",  password = "123456")

db.session.add_all([address1, address2, address3, address4])
db.session.commit()

Dog_Owner.update_address("kate@email.com", "4337 Kenilworth Avenue")
Dog_Owner.update_address("kevin@email.com", "202 Park Road")

Dog_Walker.update_address("randon@email.com", "112 Poplar Street")
Dog_Walker.update_address("beth@email.com", "905 S Sharon Amity")

dog1 = Dog(dog_owner_id = 1, first_name = "buzz", breed = "Lhasa Apso", weight = 18, age = 4, description = "Very easy going dog")
dog2 = Dog(dog_owner_id = 2, first_name = "tony", breed = "Poodle", weight = 10, age = 3, description = "Loves to eat")

message1 = Message(dog_owner_id = 1, dog_walker_id = 1, text = "Hi, how are you?")
message2 = Message(dog_owner_id = 1, dog_walker_id = 1, text = "Hi, can we talk")
message3 = Message(dog_owner_id = 1, dog_walker_id = 2, text = "bye bye")
message4 = Message(dog_owner_id = 1, dog_walker_id = 2, text = "thanks for everything")
message5 = Message(dog_owner_id = 1, dog_walker_id = 3, text = "have a great day")

appointment1 = Appointment(dog_owner_id = 1, dog_walker_id = 1, date = "2021-02-19", time_start = "03:00", duration="15", day_period ="PM")
appointment2 = Appointment(dog_owner_id = 2, dog_walker_id = 1, date = "2021-02-28", time_start = "05:00", duration="15", day_period = "PM")
appointment3 = Appointment(dog_owner_id = 1, dog_walker_id = 1, date = "2021-02-03", time_start = "01:00", duration="15", status = True, day_period = "PM")

db.session.add_all([dog1, dog2, message1, message2, message3, message4, message5, appointment1, appointment2, appointment3])
db.session.commit()