from flask import request, jsonify, Blueprint
import uuid
import os

from .models import db, Job, Tracker, Notification
from .service import fetch_jobs_from_companies, task_queue, set_expired_trackers
from .sources import companies

bp = Blueprint('main', __name__, url_prefix='/api')

company_links = {company['name']: company['link'] for company in companies}
rq_dashboard = os.environ.get('RQ_DASHBOARD', 'http://localhost:9181')

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

@bp.route('/company-links')
def get_company_links():
    return success_response(company_links)

@bp.route('/jobs')
def jobs():
    jobs = Job.query.filter(Job.is_removed == False).all()
    return success_response([job.to_dict() for job in jobs])

@bp.route('/tracker', methods=['POST'])
def create_tracker():
    if not request.json:
        return error_response("Bad Request", "Request body must be a JSON object with 'keyword', 'email', and 'duration' keys", 400)

    token = request.json.get('token')
    keyword = request.json.get('keyword')
    email = request.json.get('email')
    duration = request.json.get('duration')

    if not token or not isinstance(token, str):
        return error_response("Bad Request", "Token must be a string", 400)
    
    if not keyword or not isinstance(keyword, str):
        return error_response("Bad Request", "Keyword must be a string", 400)
    
    if not email or not isinstance(email, str):
        return error_response("Bad Request", "Email must be a string", 400)
    
    if not duration or not isinstance(duration, int):
        return error_response("Bad Request", "Duration must be an integer", 400)

    secret = str(uuid.uuid4())
    new_tracker = Tracker(token=token, secret=secret, keyword=keyword, email=email, duration=duration)
    db.session.add(new_tracker)
    db.session.commit()
    return success_response({'secret': secret})

@bp.route('/tracker/<secret>', methods=['GET'])
def view_tracker(secret):
    if not secret or not isinstance(secret, str):
        return error_response("Bad Request", "Secret must be a string", 400)
    
    tracker = Tracker.query.filter_by(secret=secret).first()
    if not tracker:
        return error_response("Not Found", "Tracker not found", 404)
    return success_response(tracker.to_dict())

@bp.route('/tracker/<secret>', methods=['DELETE'])
def delete_tracker(secret):
    if not secret or not isinstance(secret, str):
        return error_response("Bad Request", "Secret must be a string", 400)
    
    tracker = Tracker.query.filter_by(secret=secret).first()
    if tracker:
        tracker.is_removed = True
        tracker.date_removed = db.func.now()
        db.session.commit()
        return success_response()
    return error_response("Not Found", "Tracker not found", 404)

## for admin

@bp.route('/rq-dashboard')
def get_rq_dashboard():
    return success_response(rq_dashboard)


def is_admin(token):
    return token == "admin-secret-token"

@bp.route('/emails', methods=['POST'])
def all_emails():
    if not request.json:
        return error_response("Bad Request", "Request body must be a JSON object with 'token' key", 400)
    
    token = request.json.get('token')
    if not token or not isinstance(token, str):
        return error_response("Bad Request", "Token must be a string", 400)

    # TODO: implement token logic
    am_admin = is_admin(token)
    if am_admin:
        notifications = Notification.query.all()
    else:
        notifications = Notification.query.filter_by(token=token).all()

    return success_response([notification.to_dict(am_admin) for notification in notifications])

@bp.route('/trackers', methods=['POST'])
def all_trackers():
    if not request.json:
        return error_response("Bad Request", "Request body must be a JSON object with 'token' key", 400)
    
    token = request.json.get('token')
    if not token or not isinstance(token, str):
        return error_response("Bad Request", "Token must be a string", 400)

    # TODO: implement token logic
    am_admin = is_admin(token)
    if am_admin:
        trackers = Tracker.query.all()
    else:
        trackers = Tracker.query.filter_by(token=token).all()

    return success_response([tracker.to_dict(am_admin) for tracker in trackers])

@bp.route('/all-jobs')
def all_jobs():
    jobs = Job.query.all()
    return success_response([job.to_dict(True) for job in jobs])

@bp.route('/stats')
def stats():
    total_jobs = Job.query.count()
    total_trackers = Tracker.query.count()
    total_notifications = Notification.query.count()
    return success_response({
        "total_jobs": total_jobs,
        "total_trackers": total_trackers,
        "total_notifications": total_notifications
    })

@bp.route('/sync')
def force_fetch_jobs():
    task_queue.enqueue(set_expired_trackers)
    task_queue.enqueue(fetch_jobs_from_companies)
    return success_response("Syncing")

def init_app(app):
    if app.debug:
        # if debug mode is enabled, allow CORS
        from flask_cors import CORS
        CORS(app)
    # else:
    #     # when run in production, serve the frontend from the build directory /var/www/html
    #     app.static_folder = '/var/www/html'
    #     # app.static_folder = '/home/user/playground/job_tracker/job_tracker/frontend/dist'
    #     @app.route('/')
    #     def index():
    #         return app.send_static_file('index.html')
    #     @app.route('/<path:path>')
    #     def send_js(path):
    #         return app.send_static_file(path)
        
    app.register_blueprint(bp)