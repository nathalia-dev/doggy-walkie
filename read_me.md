#Doggy Walkie

### 1) Project Tech Specs:

- Language: Python 3.7.7
- Framework: Flask
- Database - PSQL
- Boostrap 4.4


### 2) Running the aplicattion:

- the requirements.txt file has all the dependecies necessary to run the application. 

- Inside the folder that has the project, create de Virtual Enviroment.  In your terminal write:
	- python -m venv venv

- After created the venv, open it. In your terminal write:
	- source venv/bin/activate

- With the venv opened, its time to install all the dependecies. In your terminal write:
	- pip intall -r requirements.txt

- now is time to run the application. In your terminal write:
	- flask run

_(Don't forget to create your database and run the seed.py file, if you want.)_

### 3) Users Rules:

- The only thing that a not login person can do is to search for dog walker. They will be not allowed to see the entire profile. But only some informations

- When sign in, the user must choose betwwen a dog walker or dog owner, using the switch button.

- The users dont need to add an address. But this is important to the dog walker, because without an address, nobody will know about where the dog_walker works. 

- The dog walker could use the description to write about his service.

- Dog owners could add dogs. It is required to inform the name, breed, age and weight. The dog owner could use the dog description field to describe his dog behavior.

- To start to communicate, the dog owner must send the first message to the dog walker. The oposite is not allowed. Only after the first message, the dog_walker can look the dog owner profile and also create an appointment. 

- Only the dog walker is allowed to cancel the appointment. 

- Only "done appointments" could be reviewed.

- When the appointment was done/completed, the dog walker must to mark as a done appointment in the system. That way, the dog owner will be able to review the appointment.

- Once the dog owner rated the appointment, it will count as the dog walker rate. 

- The rate math is super simple: we sum all the rates values and divide by the number of appointments already reviewed. This average will be the dog_walker rate. 

### 4) External API:

- For add a dog in your profile , the application gets information in an External API called TheDogApi.

- Link for the docs: https://docs.thedogapi.com/


### 5) Tests:

- to run the tests, open the project folder, open the venv, as already explained before, and write in your terminal:

	- python -m unittest -v test_file.name.py

_(Don't forget to create your test database.)_
