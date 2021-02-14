import os
import requests
import config

from flask import Flask, render_template, request, flash, redirect, session, g, Response
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from functions import is_worker, calculate_dog_walker_rate
from models import db, connect_db, Dog_Owner, Dog_Walker, Address, Dog, Message, Appointment, Review
from forms import UserAddForm, LoginForm, Dog_Owner_Profile_Form, Dog_Walker_Profile_Form, Address_Form, Dog_Form, Edit_Dog_Form, New_Message_Form, New_Appointment_Form, Review_Form

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgres:///doggy_walkie'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', config.secret)
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.before_request

def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:

        if session["is_worker"]:
            g.user = Dog_Walker.query.get(session[CURR_USER_KEY])

        else:
            g.user = Dog_Owner.query.get(session[CURR_USER_KEY])
    
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id
    session["is_worker"] = is_worker(user)


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        del session["is_worker"]

@app.route("/")
def home():
    """Home route."""

    if g.user and is_worker(g.user):
        return redirect(f"/dog_walkers/{g.user.id}")
    
    elif g.user:
        return redirect(f"/dog_owners/{g.user.id}")

    else:
        return render_template("home.html")


@app.route("/dog_walkers")
def search():
    """Handle the search for dog_walkers"""

    search = request.args.get("q")
    
    if not search:
        dog_walkers = Dog_Walker.query.all()

    else:
        dog_walkers = Dog_Walker.query.filter(Dog_Walker.name.like(f"%{search}%")).all()
    
    
    return render_template("search.html", dog_walkers = dog_walkers)


@app.route("/login",methods=["GET","POST"])
def login():
    """Handle both users login"""

    if (g.user):
        flash("You are already loged in", "danger")
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():

        if (form.dog_walker_check.data): 
            user = Dog_Walker.authenticate(form.email.data, form.password.data)
        
        else:
            user = Dog_Owner.authenticate(form.email.data, form.password.data)
        
        if user:

            do_login(user)

            if is_worker(user):
                flash(f"Hello worker, {user.name}!", "success")
                
                return redirect(f"/dog_walkers/{user.id}")
            else:
                flash(f"Hello, {user.name}!", "success")
                
                return redirect(f"/dog_owners/{user.id}")
        
       
        flash("Invalid Credentials", "danger")

        
    return render_template("login.html", form = form)



@app.route("/logout",methods=["GET"])
def logout():
    """Handle both users logout."""

    do_logout()

    return redirect("/")

@app.route("/signup", methods =["GET", "POST"])
def signup():
    """Handle both users signup."""

    form = UserAddForm()

    if form.validate_on_submit():

        try:
            if (form.dog_walker_check.data): 
                user = Dog_Walker.signup(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
                db.session.commit()
            
            else:
                user = Dog_Owner.signup(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
                db.session.commit()
        
        except IntegrityError:
            flash("Email already taken", 'danger')
            return render_template('signup.html', form=form)
            
        do_login(user)

        if is_worker(user):
            flash(f"Hello worker, {user.name}!", "success")
            return redirect(f"/dog_walkers/{user.id}")

        else:
            flash(f"Hello, {user.name}!", "success")
            return redirect(f"/dog_owners/{user.id}")
        
       
        flash("Invalid Credentials", "danger")

        
    return render_template("signup.html", form = form)


##################################################
# Dog_Walker routes

@app.route("/dog_walkers/<int:dog_walker_id>")
def dog_walker_view_page(dog_walker_id):
    """Dog_walker user page."""

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    dog_walker = Dog_Walker.query.get_or_404(dog_walker_id)

    return render_template("/dog_walker/dog_walker_home.html", user = dog_walker)

@app.route("/dog_walkers/<int:dog_walker_id>/address", methods = ["GET", "POST"])
def address_dog_walker(dog_walker_id):
    """Save an address in dog_walker profile"""

    if not g.user or not g.user.id == dog_walker_id or not is_worker(g.user):

            flash("Access Unauthorized ", "danger")
            return redirect ("/")
    
    dog_walker = Dog_Walker.query.get_or_404(dog_walker_id)
    form = Address_Form(obj=dog_walker.address)

    if form.validate_on_submit():

        if dog_walker.address is None:

            address = Address(address = form.address.data, zipcode = form.zipcode.data, city = form.city.data, state  = form.state.data, neighbor = form.neighbor.data)
            db.session.add(address)
            db.session.commit()

            if g.user.id == dog_walker_id and is_worker(g.user):

                Dog_Walker.update_address(dog_walker.email, address.address)
                flash("Address saved.", "success")
        else:

            address = Address.query.get(g.user.address.id)
            
            address.address = form.address.data
            address.zipcode = form.zipcode.data
            address.city = form.city.data
            address.state = form.state.data
            address.neighbor = form.neighbor.data

            db.session.add(address)
            db.session.commit()

        return redirect(f"/dog_walkers/{dog_walker_id}")

    return render_template("add_address.html", form = form)

@app.route("/dog_walkers/profile", methods = ["GET", "POST"])
def dog_walker_profile():
    """Update dog_walker profile"""

    if not g.user or not is_worker(g.user):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    dog_walker = g.user


    form = Dog_Walker_Profile_Form(obj = dog_walker)

    if form.validate_on_submit():

        if not Dog_Walker.authenticate(g.user.email, form.password.data):
            flash("Incorrect password - Impossible to edit profile.", "danger")
            return redirect("/")
        
        dog_walker.first_name = form.first_name.data
        dog_walker.last_name = form.last_name.data
        dog_walker.email = form.email.data
        dog_walker.cellphone = form.cellphone.data
        dog_walker.description = form.description.data
        dog_walker.photo = form.photo.data

        try:

            db.session.add(dog_walker)
            db.session.commit()
        
        except IntegrityError:
            flash("Email already taken.", 'danger')
            return render_template("dog_walker/dog_walker_edit_profile.html", form = form)


        return redirect(f"/dog_walkers/{g.user.id}")

    else:
        return render_template("dog_walker/dog_walker_edit_profile.html", form = form)


@app.route("/dog_walkers/delete", methods = ["POST"])
def delete_dog_walkers():
    """Delete your profile and your address"""

    dog_walker = Dog_Walker.query.get_or_404(g.user.id)

    if not g.user or not is_worker(g.user):
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    if g.user.address:

        address = Address.query.get(dog_walker.address.id)
        db.session.delete(address)
    
    if g.user.message:

        messages = Message.query.filter_by(dog_walker_id = dog_walker.id).all()
        for msg in messages:
            db.session.delete(msg)
    
    if g.user.appointments:

        appointments = Appointment.query.filter_by(dog_walker_id = dog_walker.id).all()
        for aptment in appointments:
            db.session.delete(aptment
            )

    db.session.delete(g.user)
    db.session.commit()

    flash(f"The user was deleted.", "success")
    return redirect("/signup")

##################################################
# Dog_Walker Message routes

@app.route("/dog_walkers/<int:dog_walker_id>/messages")
def dog_walker_messages(dog_walker_id):
    """Show all user's messages"""

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_walker_id and is_worker(g.user):

        dog_walker = Dog_Walker.query.get_or_404(dog_walker_id)
        messages = Message.query.filter_by(dog_walker_id = dog_walker_id).all()

        user_list = [msg.dog_owner for msg in messages]
        user_list = set(user_list)

        return render_template("dog_walker/dog_walker_messages.html", user_list = user_list, user = dog_walker)

    else:
        flash("Access unathorized ", "danger")
        return redirect ("/")

##################################################
# Dog_Walker Appointment routes
@app.route("/dog_walkers/<int:dog_walker_id>/appointments")
def dog_walker_appointments(dog_walker_id):
    """Show all user's appointments """

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_walker_id and is_worker(g.user):

        dog_walker = Dog_Walker.query.get_or_404(dog_walker_id)
        appointments = Appointment.query.filter_by(dog_walker_id = dog_walker.id).order_by('date').all()
    
        return render_template("dog_walker/dog_walker_appointments.html", appointments = appointments, user = dog_walker)

    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")

@app.route("/dog_walkers/<int:dog_walker_id>/done_appointments")
def dog_walker_done_appointments(dog_walker_id):
    """Show all user's accomplished appointments """

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_walker_id and is_worker(g.user):

        dog_walker = Dog_Walker.query.get_or_404(dog_walker_id)
        appointments = Appointment.query.filter_by(dog_walker_id = dog_walker.id).order_by('date').all()
    
        return render_template("dog_walker/dog_walker_done_appointments.html", appointments = appointments, user = dog_walker)

    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")   

##################################################
# Dog_Owners routes

@app.route("/dog_owners/<int:dog_owner_id>")
def dog_owner_view_page(dog_owner_id):
    """Dog_owner user page. Only the dog_walkers who already exchange messages with this person can see the profile"""

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    dog_owner = Dog_Owner.query.get_or_404(dog_owner_id)
    dog_walker_with_messages = [msg.dog_walker for msg in dog_owner.message]
    

    if (g.user.id == dog_owner_id and not is_worker(g.user)) or g.user in dog_walker_with_messages:
        
        return render_template("/dog_owner/dog_owner_home.html", user = dog_owner)
    
    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")

    

@app.route("/dog_owners/<int:dog_owner_id>/address", methods = ["GET", "POST"])
def address_dog_owner(dog_owner_id):
    """Save an address in dog_owner profile"""

    if not g.user or not g.user.id == dog_owner_id or is_worker(g.user):

        flash("Access Unauthorized ", "danger")
        return redirect ("/")
    
    dog_owner = Dog_Owner.query.get_or_404(dog_owner_id)
    form = Address_Form(obj=dog_owner.address)

    if form.validate_on_submit():

        if g.user.address == None:

            address = Address(address = form.address.data, zipcode = form.zipcode.data, city = form.city.data, state  = form.state.data, neighbor = form.neighbor.data)
            
            db.session.add(address)
            db.session.commit()

            if g.user.id == dog_owner_id and not is_worker(g.user):

                Dog_Owner.update_address(dog_owner.email, address.address)
                flash("Address saved.", "success")
        
        else:

            address = Address.query.get(g.user.address.id)
            
            address.address = form.address.data
            address.zipcode = form.zipcode.data
            address.city = form.city.data
            address.state = form.state.data
            address.neighbor = form.neighbor.data

            db.session.add(address)
            db.session.commit()

        return redirect(f"/dog_owners/{dog_owner_id}")

    return render_template("add_address.html", form = form)

@app.route("/dog_owners/profile", methods = ["GET", "POST"])
def dog_owner_profile():
    """Update dog_owner profile"""

    if not g.user or is_worker(g.user):
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    dog_owner = g.user

    form = Dog_Owner_Profile_Form(obj = dog_owner)

    if form.validate_on_submit():

        if not Dog_Owner.authenticate(g.user.email, form.password.data):
            flash("Incorrect password - Impossible to edit profile.", "danger")
            return redirect("/")
        
        dog_owner.first_name = form.first_name.data
        dog_owner.last_name = form.last_name.data
        dog_owner.email = form.email.data
        dog_owner.cellphone = form.cellphone.data
        dog_owner.photo = form.photo.data

        try:

            db.session.add(dog_owner)
            db.session.commit()
        
        except IntegrityError:
            flash("Email already taken.", 'danger')
            return render_template("dog_owner/dog_owner_edit_profile.html", form = form)

        return redirect(f"/dog_owners/{g.user.id}")

    else:
        return render_template("dog_owner/dog_owner_edit_profile.html", form = form)

@app.route("/dog_owners/delete", methods = ["POST"])
def delete_dog_owners():
    """Delete dog_owners profile and his/her address"""

    dog_owner = Dog_Owner.query.get_or_404(g.user.id)

    if not g.user or is_worker(g.user):
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    if g.user.address:
        address = Address.query.get(dog_owner.address.id)
        db.session.delete(address)
    
    if g.user.dog:
        dogs = Dog.query.filter_by(dog_owner_id = dog_owner.id).all()
        for dog in dogs:
            db.session.delete(dog)
    
    if g.user.message:
        messages = Message.query.filter_by(dog_owner_id = dog_owner.id).all()
        for msg in messages:
            db.session.delete(msg)
    
    if g.user.appointments:
        appointments = Appointment.query.filter_by(dog_owner_id = dog_owner.id).all()
        for aptment in appointments:
            db.session.delete(aptment)


    db.session.delete(g.user)
    db.session.commit()

    flash(f"The user was deleted.", "success")
    return redirect("/signup")

##################################################
# Dogs_Owners - Dogs routes

@app.route("/dog_owners/<int:dog_owner_id>/dogs")
def show_user_dogs(dog_owner_id):
    """Show the dog_owners dogs. Only the dog_owner can see and the dog_walkers that has receive messages form the dog_owner."""
    
    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")
    
    dog_walker_with_messages = [msg.dog_walker for msg in Dog_Owner.query.get_or_404(dog_owner_id).message]

    if (g.user.id == dog_owner_id and not is_worker(g.user)) or g.user in dog_walker_with_messages:

        dog_owner = Dog_Owner.query.get_or_404(dog_owner_id)
    
        dogs = dog_owner.dog
        

        return render_template("dog_owner/dog_owner_dogs.html", dogs = dogs, user = dog_owner)
    
    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")

@app.route("/dog_owners/<int:dog_owner_id>/dogs/add", methods = ["GET", "POST"])
def add_dogs(dog_owner_id):
    """Add dogs to the application."""

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_owner_id and not is_worker(g.user):

        form = Dog_Form()

        # requesting an external API to fullfield the breed options.
        params = {
            "x-api-key": config.api_key
        }

        res = requests.get("https://api.thedogapi.com/v1/breeds", params=params)
        data = res.json()
        
        breed_list = [(result["name"], result["name"]) for result in data]
        breed_list.append(("Other", "Other"))
        form.breed.choices = breed_list
        

        if form.validate_on_submit():
            dog = Dog(dog_owner_id = dog_owner_id, first_name = form.first_name.data, breed = form.breed.data, weight = form.weight.data, age = form.age.data)
            
            db.session.add(dog)
            db.session.commit()

            # requesting an external API to automatically create a dog description, based on the chose breed.
            dog = Dog.query.filter_by(first_name = form.first_name.data).first()

            if dog.breed != "Other":
                res = requests.get(f"https://api.thedogapi.com/v1/breeds/search?q={dog.breed}", params=params)
                data = res.json()
                dog.description = data[0]["temperament"]
            
                db.session.add(dog)
                db.session.commit()

            flash("Dog added", "success")
            return redirect(f"/dog_owners/{dog_owner_id}/dogs")
        
        else:
            return render_template("dogs/add_dog.html", form = form)

    
    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")

##################################################
# Dogs_Owners - Messages routes

@app.route("/dog_owners/<int:dog_owner_id>/messages")
def dog_owner_messages(dog_owner_id):
    """Show all messages for that dog_owner user"""

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_owner_id and not is_worker(g.user):

        dog_owner = Dog_Owner.query.get_or_404(dog_owner_id)
        messages = Message.query.filter_by(dog_owner_id = dog_owner_id).all()

        user_list = [msg.dog_walker for msg in messages]
        user_list = set(user_list)

        return render_template("dog_owner/dog_owner_messages.html", user_list = user_list, user = dog_owner)

    else:
        flash("Access unathorized ", "danger")
        return redirect ("/")

##################################################        
# Dog_Owners - Appointment routes

@app.route("/dog_owners/<int:dog_owner_id>/appointments")
def dog_owner_appointments(dog_owner_id):
    """Show all user's appointments """

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_owner_id and not is_worker(g.user):

        dog_owner = Dog_Owner.query.get_or_404(dog_owner_id)
        appointments = Appointment.query.filter_by(dog_owner_id = dog_owner.id).order_by('date').all()
        return render_template("dog_owner/dog_owner_appointments.html", appointments = appointments, user = dog_owner)

    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/") 

@app.route("/dog_owners/<int:dog_owner_id>/done_appointments")
def dog_owner_done_appointments(dog_owner_id):
    """Show all user's accomplished appointments """

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_owner_id and not is_worker(g.user):
        
        dog_owner = Dog_Owner.query.get_or_404(dog_owner_id)
        appointments = Appointment.query.filter_by(dog_owner_id = dog_owner.id).order_by('date').all()

        return render_template("dog_owner/dog_owner_done_appointments.html", appointments = appointments, user = dog_owner)

    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/") 

##################################################
# Dogs routes

@app.route("/dogs/<int:dog_id>")
def show_dog_details(dog_id):
    """Show dog details: only the dog_owner and the dog_walkers who already exchange messages with the owners can see"""

    dog = Dog.query.get_or_404(dog_id)
    dog_owner = dog.dog_owner

    #catching the dog_walkers who already exchange messages with the dog_owners,so they can see dog profile.
    dog_walker_with_messages = [msg.dog_walker for msg in dog_owner.message]

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if (g.user.id == dog_owner.id and not is_worker(g.user)) or g.user in dog_walker_with_messages:

        return render_template("dogs/show_dog.html", dog = dog)
    
    else:

        flash("Access Unauthorized ", "danger")
        return redirect ("/")
    
    

@app.route("/dogs/<int:dog_id>/edit",methods = ["GET", "POST"])
def edit_dog_details(dog_id):
    """Edit dog details"""

    dog = Dog.query.get_or_404(dog_id)
    dog_owner = dog.dog_owner

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_owner.id and not is_worker(g.user):
    
        form = Edit_Dog_Form(obj = dog)

        # requesting an external API to fullfield the breeds options.
        params = {
            "x-api-key": config.api_key
        }

        res = requests.get("https://api.thedogapi.com/v1/breeds", params=params)
        data = res.json()
        breed_list = [(result["name"], result["name"]) for result in data]
        breed_list.append(("Other", "Other"))
        form.breed.choices = breed_list

        if form.validate_on_submit():

            dog.first_name = form.first_name.data
            dog.breed = form.breed.data
            dog.weight = form.weight.data
            dog.age = form.age.data
            dog.color  = form.color.data
            dog.description = form.description.data
            dog.photo = form.photo.data

            db.session.add(dog)
            db.session.commit()

            flash("Dog updated.", "success")
            return redirect(f"/dogs/{dog_id}")
        
        else:
            return render_template("dogs/edit_dog.html", form = form)
    
    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")

@app.route("/dogs/<int:dog_id>/delete",methods = ["POST"])
def delete_dog_details(dog_id):
    """Delete dog profile"""

    dog = Dog.query.get_or_404(dog_id)
    dog_owner = dog.dog_owner

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")

    if g.user.id == dog_owner.id and not is_worker(g.user):
    
       db.session.delete(dog)
       db.session.commit()

       return redirect(f"/dog_owners/{dog_owner.id}/dogs")
    
    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")

##################################################
# Message Routes

@app.route("/messages/<int:dog_owner_id>/<int:dog_walker_id>", methods=["GET", "POST"])
def messages_between_users(dog_owner_id, dog_walker_id):
    """Route to show and create messages between tow users"""

    if not g.user:
        flash("You need to login first ", "danger")
        return redirect ("/")
    

    dog_owner = Dog_Owner.query.get_or_404(dog_owner_id)
    dog_walker = Dog_Walker.query.get_or_404(dog_walker_id)

    messages = Message.query.filter_by(dog_owner_id = dog_owner_id, dog_walker_id = dog_walker_id).all()
    dog_walkers_messages = [msg.dog_walker for msg in messages]


    # the dog_walker user only can send messages to dog_owners, if the dog_owner has already sent a message for him before.
    if is_worker(g.user): 
        if g.user not in dog_walkers_messages:
            flash("Access Unauthorized ", "danger")
            return redirect ("/")


    if g.user.id == dog_owner_id or g.user.id == dog_walker_id:

        form = New_Message_Form()

        if form.validate_on_submit():

            new_message = Message(dog_owner_id = dog_owner.id, dog_walker_id = dog_walker.id, is_sender_worker = is_worker(g.user), text = form.text.data)
            db.session.add(new_message)
            db.session.commit()

            return redirect(f"/messages/{dog_owner.id}/{dog_walker.id}")
    
    
        else:
            return render_template("messages_between_users.html", messages = messages, dog_walker = dog_walker, dog_owner = dog_owner, form = form)

    else:
        flash("Access Unauthorized ", "danger")
        return redirect ("/")

##################################################
# Appointment Routes

@app.route("/appointments/<int:aptment_id>/change_status", methods=["POST"])
def change_appointment_status(aptment_id):
    """Route for the dog_walker change the appointment status to done"""

    aptment =  Appointment.query.get_or_404(aptment_id)
   
    if g.user.id == aptment.dog_walker.id:
        
        aptment.status = True

        db.session.add(aptment)
        db.session.commit()

        return redirect(f"/dog_walkers/{aptment.dog_walker.id}/appointments")


    else:
        flash("Access Unauthorized", "danger")
        return redirect("/")

@app.route("/appointments/new", methods = ["GET", "POST"])
def create_appointment():
    """ Route to create an appointment: only dog_walker can do"""

    if is_worker(g.user):
        form = New_Appointment_Form()

        # catching all the dog_owners that has sent a message to our dog_worker.
        dog_owners = [msg.dog_owner for msg in g.user.message]
        

        form.day_period.choices = [("AM", "AM"), ("PM", "PM")]
        form.dog_owner_id.choices = [(user.id, user.name) for user in set(dog_owners)]

        if form.validate_on_submit():
            newAptment = Appointment(dog_walker_id = g.user.id,dog_owner_id = form.dog_owner_id.data, date = form.date.data, time_start = form.time_start.data, day_period = form.day_period.data, duration = form.duration.data)
            
            db.session.add(newAptment)
            db.session.commit()

            return redirect(f"/dog_walkers/{g.user.id}/appointments")
        
        else:
            return render_template("add_appointment.html", form = form)

    else:
        flash("Access Unauthorized", "danger")
        return redirect("/")

@app.route("/appointments/<int:aptment_id>/delete", methods=["POST"])
def delete_appointment(aptment_id):
    """ Route to delete an appointment: only dog_walker can do"""

    aptment =  Appointment.query.get_or_404(aptment_id)
    
    if g.user.id == aptment.dog_walker.id:

        if not aptment.status:
        
            db.session.delete(aptment)
            db.session.commit()

        return redirect(f"/dog_walkers/{aptment.dog_walker.id}/appointments")


    else:
        flash("Access Unauthorized", "danger")
        return redirect("/")


##################################################
# Review Routes

@app.route("/review/<int:aptment_id>", methods=["POST", "GET"])
def review_appointment(aptment_id):
    """Review the appointment: for dog_owner"""

    if not g.user:
        flash("You need to login first.", "danger")
        return redirect ("/")
    
    appointment = Appointment.query.get_or_404(aptment_id)
    dog_walker = Dog_Walker.query.get(appointment.dog_walker_id)

    if appointment.review or appointment.status == False:
            flash("Access Unauthorized.", "danger")
            return redirect ("/")

    if g.user.id == appointment.dog_owner.id and not is_worker(g.user):

        form = Review_Form()
        form.rate.choices = [(1,1),(2,2),(3,3), (4,4), (5,5)]

        if form.validate_on_submit():

                review = Review(appointment_id = aptment_id, rate = form.rate.data, comment = form.comment.data)
                db.session.add(review)
                db.session.commit()

                calculate_dog_walker_rate(db, dog_walker)

                return redirect(f"/dog_owners/{g.user.id}/done_appointments")

        else:

            return render_template("add_review.html", form = form, aptment = appointment)
    
    else:
        flash ("Access Unauthorized.", "danger")
        return redirect("/")

##################################################
# 404 Route

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404_page.html'), 404