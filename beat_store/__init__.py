import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask


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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    

    from . import db
    db.init_app(app)

    @app.route('/')
    def home():
        from flask import redirect, url_for
        return redirect(url_for('beats.beat_library'))


    from . import beats
    app.register_blueprint(beats.bp)
    # app.add_url_rule('/', endpoint='beat_library')


    from . import admin
    app.register_blueprint(admin.bp)


    from . paypal import processing_orders
    app.register_blueprint(processing_orders.bp)


    from . import test_queue
    app.register_blueprint(test_queue.bp)


    return app


def get_domain():
    from flask import request
    domain = request.root_url[:-1]
    return domain
