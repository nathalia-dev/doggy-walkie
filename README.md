# Doggy Walkie

### Description

Doggy Walkie is a full stack application that provides the connection between 2 different users: the *dog owner* and the *dog walker*. 

There are two goals: 

- to facilite the search for a *dog walk* service.
- to provide a place where anybody could earn an extra income. 

### Project Tech Specs:

- Language: Python 3.7.7
- Framework: Flask
- Database - PostgreSQL
- Boostrap 4.4


### Usage 🚀:

- Inside the folder that has the project, create the Virtual Enviroment.  In your terminal run: `python -m venv venv`.

- After create the venv, open it. To do it, run: `source venv/bin/activate`.

- The `requirements.txt` file has all the dependecies necessary to run the application. So, once you already have the venv opened, it's time to install all the dependecies. In your terminal run: `pip intall -r requirements.txt`.

- Now, it's time to run the application. In your terminal, run: `flask run`.

_(Don't forget to create your database and run the seed.py file, if you want.)_

### Users Rules:

- The only thing that a not login person can do is to search for dog walker. They will be not allowed to see the entire profile. But only some informations

- When sign in, the user must choose betwwen a dog walker or dog owner, using the switch button.

- The users don't need to add an address. But this is important to the dog walker, because without an address, nobody will know about where the dog_walker works. 

- The dog walker could use the description to write about his/her service.

- Dog owners can add dogs. It is required to inform the name, breed, age and weight. The dog owner can use the dog description field to describe his/her dog behavior.

- To start to communicate, the dog owner must send the first message to the dog walker. The oposite is not allowed. Only after the first message, the dog_walker can look the dog owner's profile and also creates an appointment. 

- Only the dog walker is allowed to cancel the appointment. 

- Only "done appointments" could be rated/reviewed.

- When the appointment was done/completed, the dog walker must mark as a *done appointment* in the system. That way, the dog owner will be able to review the appointment.

- Once the dog owner rated the appointment, it will count as the dog walker rate. 

- The rate math is super simple: It sum all the rates values and divide by the number of appointments already reviewed. This average will be the dog_walker rate. 

### External API:

- For add a dog in your profile , the application gets information in an External API called TheDogApi.

- Link for the docs: https://docs.thedogapi.com/


### Tests:

- to run the tests, open the project folder, open the venv, as already explained before, and run in your terminal: `python -m unittest -v test_file.name.py`.

_(Don't forget to create your test database.)_
