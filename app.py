from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

# from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User
from forms import RegisterForm, LoginForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///flask_feedback_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "shhhhh"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def homepage():
    """Homepage of site; redirect to register."""

    return redirect("/register")

@app.route("/register", methods=['GET', 'POST'])
def register_form():
  form = RegisterForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data

    new_user = User.register(username, password, email, first_name, last_name)
    db.session.add(new_user)
    try:
      db.session.commit()
    except IntegrityError:
      form.username.errors.append('Username or email already in use')
      return render_template('register.html', form=form)
    session['curr_user_id'] = new_user.username
    flash(f'Welcome to the secret page {username}')
    return redirect('/secret')
  return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_form():
  form = LoginForm()

  return render_template('login.html', form=form)

@app.route('/secret')
def secret_page():
  return render_template('secret.html')
