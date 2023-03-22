import os
from flask import Flask

def create_app(test_config=None):
    # creating the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'kanbanr.sqlite'),
    )

    if test_config is None:
        # using an instance
        app.config.from_pyfile('config.py', silent=True)
    else:
        # or testing
        app.config.from_mapping(test_config)

    # making the instance folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #for testing
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    #importing all the necessary modules
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import board
    app.register_blueprint(board.bp)
    app.add_url_rule('/', endpoint='index')

    return app

app = create_app() 