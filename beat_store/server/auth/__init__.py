from flask import Blueprint, flash, request, abort, redirect, render_template, url_for, current_app
from flask_login import login_user, UserMixin, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

from ... db import get_db


class User(UserMixin):

    def __init__(self, id, username, email, password):

        self.id = id
        self.username = username
        self.email = email
        self.password = password


@bp.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False


        with current_app.app_context():

            db = get_db()
            cursor = db.cursor()

            row_data = cursor.execute('SELECT id, username, email, password FROM user WHERE username == ?', (username,)).fetchone()

            # Pretty sure this is a super convuleted way to do this, but it works. Perhaps try and improve at some point in future.
            try:

                if row_data:

                    id, username, email, password_hash = row_data
                    
                    if check_password_hash(password_hash, password):

                        user = User(id, username, email, password)
                        login_user(user, remember=remember)

                        if username.lower() == 'eventbridge':
                            return redirect(url_for('admin.update_database'))

                        next = request.args.get('next')

                        from . is_safe_url import is_safe_url
                        
                        if not is_safe_url(next):
                            return abort(400)
                        
                        return redirect(next or url_for('profile'))

                    raise Exception('Password incorrect, please try again.')
                
                raise Exception('User does not exist.')
            
            except Exception as e:
                flash(e.args[0])
                return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    
    return render_template('auth/login.html')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'POST':

        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        with current_app.app_context():

            db = get_db()
            cursor = db.cursor()

            user = cursor.execute('SELECT id FROM user WHERE username == ?', (username,)).fetchone() # if this returns an id, then the user already exists in database
        
            if user: # if a user is found, we want to redirect back to signup page so user can try again
                flash('Account already exists')
                return redirect(url_for('auth.signup'))

            # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            cursor.execute('''
                INSERT INTO user (username, password)
                VALUES (?, ?)
                ;''', (username, generate_password_hash(password, method='sha256')))

            if email:

                # Add step here to check if email is valid.

                cursor.execute('''
                    UPDATE user
                    SET email = ?
                    WHERE username = ?
                    ;''', (email, username))

            # add the new user to the database
            db.commit()


        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
