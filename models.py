"""SQLAlchemy models for Doggy-Walkie."""


from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import column_property


bcrypt = Bcrypt()
db = SQLAlchemy()

class Dog_Owner(db.Model):
    """User dog_owner in the system."""

    __tablename__ = 'dog_owner'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )

    name = column_property(first_name + " " + last_name)

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    cellphone= db.Column(
        db.String,
    )

    address_id = db.Column(
        db.Integer,
        db.ForeignKey('address.id', ondelete = "cascade"),
        nullable = True
    )

    photo = db.Column(
        db.Text, 
        default = "/static/images/profile_no_photo.jpg"
    )
    

    def __repr__(self):
        return f"<Dog_Owner User #{self.id}: {self.email}, {self.first_name} {self.last_name}>"

    @classmethod
    def signup(cls, first_name, last_name, email, password):
        """Sign up dog_owner.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        dog_owner = Dog_Owner(
            first_name=first_name,
            last_name = last_name,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(dog_owner)
        return dog_owner

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        dog_owner = cls.query.filter_by(email=email).first()

        if dog_owner:
            is_auth = bcrypt.check_password_hash(dog_owner.password, password)
            if is_auth:
                return dog_owner

        return False

    @classmethod
    def update_address(cls, email, address_string):
        """ Add the address to the user profile  """

        dog_owner = cls.query.filter_by(email = email).first()
        address = Address.query.filter_by(address = address_string).first()

        dog_owner.address_id = address.id

        db.session.add(dog_owner)
        db.session.commit()

class Dog_Walker(db.Model):
    """User dog_walker in the system."""

    __tablename__ = 'dog_walker'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )

    name = column_property(first_name + " " + last_name)

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    cellphone= db.Column(
        db.String,
    )

    address_id = db.Column(
        db.Integer,
        db.ForeignKey('address.id', ondelete = "cascade"),
        nullable = True
    )

    description = db.Column(
        db.String(450),
    )

    photo = db.Column(
        db.Text, 
        default = "/static/images/profile_no_photo.jpg"
    )

    rate = db.Column(
        db.Integer
    )

    def __repr__(self):
        return f"<Dog_Walker User #{self.id}: {self.email}, {self.first_name} {self.last_name}>"

    @classmethod
    def signup(cls, first_name, last_name, email, password):
        """Sign up dog_owner.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        dog_walker = Dog_Walker(
            first_name=first_name,
            last_name = last_name,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(dog_walker)


        return dog_walker

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        dog_walker = cls.query.filter_by(email=email).first()

        if dog_walker:
            is_auth = bcrypt.check_password_hash(dog_walker.password, password)
            if is_auth:
                return dog_walker

        return False

    @classmethod
    def update_address(cls, email, address_string):
        """ Add the address to the user profile  """
        dog_walker = cls.query.filter_by(email = email).first()
        address = Address.query.filter_by(address = address_string).first()

        dog_walker.address_id = address.id

        db.session.add(dog_walker)
        db.session.commit()


class Address(db.Model):
    """Address in the system."""

    __tablename__ = 'address'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    address = db.Column (
        db.String,
    )

    zipcode = db.Column(
        db.Integer,
        nullable = False
    )

    city = db.Column(
        db.String,
        nullable = False
    )

    state = db.Column(
        db.String,
        nullable = False
    )

    neighbor = db.Column(
        db.String,
        nullable = False
    )

    dog_owner = db.relationship("Dog_Owner", backref = "address")

    dog_walker = db.relationship("Dog_Walker", backref = "address")

    def __repr__(self):
        return f"<Address #{self.id}: {self.zipcode}, {self.city} - {self.state} >"


class Dog(db.Model):
    """Dogs in the system"""

    __tablename__ = "dog"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    dog_owner_id = db.Column(
        db.Integer,
        db.ForeignKey('dog_owner.id', ondelete = "cascade")
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    breed = db.Column(
        db.Text,
        nullable = False
    )

    weight = db.Column(
        db.Integer,
        nullable = False
    )

    age = db.Column(
        db.Integer,
        nullable = False
    )

    color = db.Column(
        db.Text,
    )

    description = db.Column(
        db.Text,
    )

    photo = db.Column(
        db.Text, 
        default = "/static/images/profile_no_photo.jpg"
    )

    dog_owner = db.relationship("Dog_Owner", backref = "dog")

    def __repr__(self):
        return f"<Dog #{self.id}: {self.first_name} - {self.breed} - Dog_Owner = {self.dog_owner.id} - {self.dog_owner.first_name} {self.dog_owner.last_name} >"


class Message(db.Model):
    """Messages in the system"""

    __tablename__ = "message"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    dog_owner_id = db.Column(
        db.Integer,
        db.ForeignKey('dog_owner.id', ondelete = "cascade")
    )

    dog_walker_id = db.Column(
        db.Integer,
        db.ForeignKey('dog_walker.id', ondelete = "cascade")
    )

    is_sender_worker = db.Column(
        db.Boolean,
        default = False,
        nullable = False
    )

    text = db.Column(
        db.String,
        nullable = False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default = datetime.utcnow()
    )

    read = db.Column(
        db.Boolean,
        default = False
    )

    dog_owner = db.relationship("Dog_Owner", backref = "message")
    dog_walker = db.relationship("Dog_Walker", backref = "message")

    def __repr__(self):
        return f"<Message #{self.id} >"

class Appointment(db.Model):
    """Appointments in the system"""

    __tablename__ = "appointment"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    dog_owner_id = db.Column(
        db.Integer,
        db.ForeignKey('dog_owner.id', ondelete = "cascade")
    )

    dog_walker_id = db.Column(
        db.Integer,
        db.ForeignKey('dog_walker.id', ondelete = "cascade")
    )

    date = db.Column(
        db.String,
        nullable = False
    )

    time_start = db.Column(
        db.String,
        nullable = False
    )

    day_period = db.Column(
        db.String,
        nullable = False
    )

    duration = db.Column(
        db.String,
        nullable = False
    )

    status = db.Column(
        db.Boolean,
        default = False
    )

    dog_owner = db.relationship("Dog_Owner", backref = "appointments")
    dog_walker = db.relationship("Dog_Walker", backref = "appointments")

    def __repr__(self):
        return f"<Appointment #{self.id} >"

class Review(db.Model):
    """Dog_Owner Review about the appointment"""

    __tablename__ = "review"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey('appointment.id', ondelete = "cascade")
    )

    rate = db.Column(
        db.Integer,
        nullable = False
    )

    comment = db.Column(
        db.String,
    )

    appointment = db.relationship("Appointment", backref = "review")
    

    def __repr__(self):
        return f"<Review #{self.id} - Rate: {self.rate} - Appointment: {self.appointment_id} >"


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)