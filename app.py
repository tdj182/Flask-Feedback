from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

# from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///flask_feedback_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "shhhhh"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def redirect_to_homepage():
    """Homepage of site; redirect to register."""

    return redirect("/homepage")


@app.route("/homepage")
def homepage():
    """Homepage of site; redirect to register."""
    all_feedback = Feedback.query.all()
    return render_template("homepage.html", feedback=all_feedback)


@app.route("/register", methods=['GET', 'POST'])
def register_form():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(
            username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username or email already in use')
            return render_template('register.html', form=form)
        session['curr_user'] = new_user.username
        flash(f'Welcome to the secret page {username}')
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back, {user.username}')
            session['curr_user'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('curr_user')
    flash("You've logged out")
    return redirect('/')


@app.route('/users/<username>')
def user_page(username):
    if 'curr_user' not in session:
        flash('Please Login first')
        return redirect('/')

    user = User.query.get_or_404(username)
    feedback = Feedback.query.filter_by(username=username)
    return render_template('user_info.html', user=user, feedback=feedback)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete a user if signed in as said user"""

    if "curr_user" not in session or session['curr_user'] != username:
        flash('You don\'t have permission to do that')
        return redirect('/')

    flash(f'User {username} has been deleted')
    Feedback.query.filter_by(username=username).delete()
    User.query.filter_by(username=username).delete()
    db.session.commit()
    session.pop('curr_user')
    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def feedback_form(username):
    """Show form or add new feedback"""
    if "curr_user" not in session or session['curr_user'] != username:
        flash('You don\'t have permission to do that')
        return redirect('/')

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(
            title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/users/{username}')

    return render_template('feedback_form.html', form=form, username=username)


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def feedback_update_form(feedback_id):
    """Show form or add new feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "curr_user" not in session or session['curr_user'] != feedback.username:
        flash('You don\'t have permission to do that')
        return redirect('/')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.username}')

    return render_template('feedback_edit.html', form=form, feedback=feedback)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Show form or add new feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "curr_user" not in session or session['curr_user'] != feedback.username:
        flash('You don\'t have permission to do that')
        return redirect('/')

    db.session.delete(feedback)
    db.session.commit()

    return redirect(f'/users/{feedback.username}')
