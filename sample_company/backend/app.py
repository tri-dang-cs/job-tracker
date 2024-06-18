#!/usr/bin/env python

from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)

# if debug mode is enabled, allow CORS
if app.debug:
    from flask_cors import CORS
    CORS(app)

company_name = os.environ.get('COMPANY_NAME', 'Sample Company')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    date_posted = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'date_posted': self.date_posted.isoformat(),
        }

sample_jobs = [
    {"title": "Cloud Engineer", "description": "Manage cloud infrastructure."},
    {"title": "AI Specialist", "description": "Develop and maintain AI models."},
    {"title": "Network Engineer", "description": "Design and maintain network infrastructure."},
    {"title": "QA Engineer", "description": "Ensure the quality of software products."},
    {"title": "UI/UX Designer", "description": "Design user interfaces and experiences."}
]

sample_locs = [
    "Los Angeles, CA",
    "Boston, MA",
    "Dallas, TX",
    "Denver, CO",
    "Miami, FL",
]

with app.app_context():
    db.create_all()
    # Check if the database is empty and add 5 random records if it is
    if Job.query.count() == 0:
        for job in sample_jobs:
            loc = random.choice(sample_locs)
            new_job = Job(
                title=job['title'],
                description=job.get('description', ""),
                location=loc,
            )
            db.session.add(new_job)
        db.session.commit()

bp = Blueprint('main', __name__, url_prefix='/api')


def success_response(data=None, message="Success", status_code=200):
    response = {
        "status": "success",
        "data": data,
        "message": message
    }
    return jsonify(response), status_code

def error_response(error="Error", message="An error occurred", status_code=400):
    response = {
        "status": "error",
        "error": error,
        "message": message
    }
    return jsonify(response), status_code

# when run in production, serve the frontend from the build directory /var/www/html
if not app.debug:
    app.static_folder = '/var/www/html'
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    @app.route('/<path:path>')
    def send_js(path):
        return app.send_static_file(path)
    
@bp.route('/company', methods=['GET'])
def get_company():
    return success_response({"name": company_name})

@bp.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    return success_response([job.to_dict() for job in jobs])

@bp.route('/jobs', methods=['POST'])
def add_job():
    if not request.json or not 'title' in request.json or not 'location' in request.json or not 'description' in request.json:
        return error_response("Bad Request", "Request body must be a JSON object with 'title', 'location', and 'description' keys", 400)
    job = Job(
        title=request.json['title'],
        description=request.json['description'],
        location=request.json['location']
    )
    db.session.add(job)
    db.session.commit()
    return success_response(job.to_dict(), "Job added successfully", 201)

@bp.route('/jobs/random', methods=['POST'])
def add_random_job():
    random_job = random.choice(sample_jobs)
    random_loc = random.choice(sample_locs)
    job = Job(
        title=random_job['title'],
        description=random_job.get('description', ""),
        location=random_loc,
    )
    db.session.add(job)
    db.session.commit()
    return success_response(job.to_dict(), "Random job added successfully", 201)

@bp.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if job is None:
        return error_response("Not Found", "Job not found", 404)
    db.session.delete(job)
    db.session.commit()
    return success_response(job.to_dict(), message="Job deleted successfully")

@bp.route('/jobs/random', methods=['DELETE'])
def delete_random_job():
    job = Job.query.order_by(db.func.random()).first()
    if job is None:
        return error_response("Not Found", "No jobs found", 404)
    db.session.delete(job)
    db.session.commit()
    return success_response(job.to_dict(), message="Random job deleted successfully")

app.register_blueprint(bp)