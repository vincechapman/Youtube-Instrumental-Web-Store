import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template

from flask_login import login_required, current_user


def get_domain():
    from flask import request
    domain = request.root_url[:-1]
    return domain


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ['FLASK_SECRET_KEY'],
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)


    # TEST PAGE FOR LOGINS

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('auth/profile.html', name=current_user.username)


    # SETTING UP LOGIN MANAGER

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from . server.auth import User

    @login_manager.user_loader
    def load_user(user_id):
        
        from . db import get_db
        db = get_db()
        cursor = db.cursor()

        row_data = cursor.execute('SELECT id, username, email, password FROM user WHERE id = ?', (user_id,)).fetchone()

        if row_data:
            id, username, email, password = row_data
            user = User(id, username, email, password)
        else:
            user = None

        return user


    # SETTING UP HOMEPAGE

    homepage = 'beats.beat_library'

    app.add_url_rule('/', endpoint=homepage)

    @app.route('/home')
    def home():
        from flask import redirect, url_for
        print(f'Current domain: {get_domain()}')
        return redirect(url_for(homepage))


    # REGISTERING BLUEPRINTS

    from . server import beats
    app.register_blueprint(beats.bp)

    from . server import admin
    app.register_blueprint(admin.bp)

    from . paypal import processing_orders
    app.register_blueprint(processing_orders.bp)

    from . server import receipt
    app.register_blueprint(receipt.bp)

    from . server import auth
    app.register_blueprint(auth.bp)


    return app
