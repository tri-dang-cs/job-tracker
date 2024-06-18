import os

from flask import Flask

from .models import db
from . import views, service


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev_key',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///dev.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REDIS_URL=os.environ.get('REDIS_URL') or 'redis://localhost:6379/0',
    )

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    @app.cli.command('truncate-db')
    def truncate_db():
        with app.app_context():
            db.drop_all()
            db.create_all()
        print('Database truncated successfully.')

    @app.cli.command('run-service')
    def run_service():
        service.run_service()

    @app.cli.command('run-worker')
    def run_worker():
        service.run_worker()

    views.init_app(app)
    service.init_app(app)

    return app