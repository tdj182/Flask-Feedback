from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
  """Connect to database."""

  db.app = app
  db.init_app(app)

class User(db.Model):

    __tablename__ = "users"

    username = db.Column(db.String(20), nullable=False, primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def __init__(self, username, password, email, first_name, last_name):
      self.username = username
      self.password = password
      self.email = email
      self.first_name = first_name
      self.last_name = last_name

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
      
      hashed =  bcrypt.generate_password_hash(pwd)
      hashed_utf8 = hashed.decode('utf8')

      return cls(username=username, password=pwd, email=email, first_name=first_name, last_name=last_name)
