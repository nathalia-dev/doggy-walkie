# Doggy Walkie

### Description

Doggy Walkie is a full stack application that provides the connection between 2 different users: the *dog owner* and the *dog walker*. 

There are two goals: 

- to facilite the search for a *dog walk* service.
- to provide a place where anybody could earn an extra income. 

### Project Tech Specs:

- Python 3.7.7
- Flask
- PostgreSQL
- Boostrap 4.4

##### Important Libraries:

- SQLAlchemy : a ORM (Object-Relational Mapping) library. 
- WTForms: a library that helps with forms validation and forms rendering.
- Jinja: a template engine. 
- Bcrypt: It helps to encrypt the user's password before send it to the database
- Unittest: standart built-in library from python to test. 


### Usage 🚀:

- First, make sure you do have `python` and `pip` installed. If you do have python 3.7.7, you will have pip also. To check your python version, please run `python --version` in your terminal.
- After this, in your terminal, execute `git clone` and make sure you're at project's root directory.
- Now you need to create the *Virtual Enviroment* (venv).  In your terminal, inside the project's root directory,  run: `python -m venv venv`.
- After create the *venv*, let's open it. To do it, run: `source venv/bin/activate`.
- The `requirements.txt` file has all the dependecies necessary to run the application. So, once you already have the *venv* opened, it's time to install all the dependecies. In your terminal run: `pip intall -r requirements.txt`.
- Now, let's go for the database part. Please, using PostgreSQL, create a database called "doggy_walkie".
- To create all the tables and populate it with an initial set of data, please from your terminal, at the he project's root directory, run: `python seed.py`. 
- Let's run the application. In your terminal, please type: `flask run`. Please, use the URL `http://localhost:5000/` .

### Project Functionalities

- The project is divided by 6 aspects: users, authentication, dogs, messages, appointments and reviews.
- There are 2 types of users: the dog_owner and the dog_walker.
- The authentication process uses the *session extension*, which enables to store user's information throughtout a session. 
- The dog_owner can create a dog profile, sharing all the important informations about the dog. The dog_walker can view those dog's profile, to better understand the dog he/she will probably walk with. 
- Both user's can exchange messages. It works as a little simple chat.
- After chating, the dog_walker can create an appointment, which will have the day and time that both user's have agreed upon. Those appointments have a status that can be done/undone. Once it is done, it enables the review feature. 
- The dow_owner can review the dog_walker service. 

### User's Rules:

- The only thing that a not login person can do is to search for a dog walker. They will not be allowed to see the entire profile. But only some informations.
- When sign in, the user must choose between a dog walker or dog owner, using the switch button.
- The users don't need to add an address. But this is important to the dog walker, because without an address, nobody will know about where the dog_walker works. 
- Dog owners can add dogs. It is required to inform the name, breed, age and weight. The dog owner can use the dog description field to describe his/her dog behavior.
- To start to communicate, by the messages feature, the dog owner must send the first message to the dog walker. The oposite is not allowed. 
- Only after the first message, the dog_walker can look the dog owner's profile and also creates an appointment ofr them. 
- Only the dog walker is allowed to cancel the appointment. 
- Only "done appointments" could be rated/reviewed.
- When the appointment was done/completed, the dog walker must mark as a *done appointment* in the system. That way, the dog owner will be able to review the appointment.
- Once the dog owner rates the appointment, it will count as the dog walker rate. 
- The rate math is super simple: It sum all the rates values and divide it by the number of appointments already reviewed. This average will be the dog_walker rate. 


### External API:

- For add a dog in the dog_owner's profile , the application gets dog's information thourght an External API, called TheDogApi.
- Link for the docs [here](https://docs.thedogapi.com/)


### Tests:

- to run the tests, first create a test database using PostgreSQL , called *doggy_walkie_test* . 
- open your terminal and go to the project's root directory.
- Open the *venv*, as already explained before, and run in your terminal the following command: `python -m unittest -v` adding in the end of it the test file name you want. e.g.: `python -m unittest -v test_anytestfilename.py`

### Future Improvements

- Redo the database's schema for users, which will improve the way that the app control if the logged in user is a dow_owner or a dog_walker. 
- Better organize the project files structure, especially inside the `app.py` file.
- Rethink the routes path structure.
- Create a new Jinja template for forms, allowing it to be reused everytime a form is necessary. 
- Implement a calendar where the dog_walker can offers days and times available , which would allow the dog_owner to enter in this calendar , choose a date/time and book an appointment. 
- Implement a live chat using WebScoket. 
