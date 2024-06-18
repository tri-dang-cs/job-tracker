import pytest

from ..app import create_app
from ..models import Job, db

@pytest.fixture
def client():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    }
    app = create_app(test_config)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            sample_jobs = [
                {'company': 'google', 'title': 'Python Developer', 'description': 'Python, Flask, SQL', 'location': 'Mountain View, CA'},
                {'company': 'google', 'title': 'Java Developer', 'description': 'Java, Spring, SQL', 'location': 'Mountain View, CA'},
                {'company': 'microsoft', 'title': 'JavaScript Developer', 'description': 'JavaScript, React, SQL', 'location': 'San Francisco, CA'},
            ]
            
            # create sample jobs
            for job in sample_jobs:
                new_job = Job(
                    company=job['company'],
                    title=job['title'],
                    description=job['description'],
                    location=job['location'],
                )
                db.session.add(new_job)
            db.session.commit()


        yield client
        with app.app_context():
            db.drop_all()
