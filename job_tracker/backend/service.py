import os
import time
from datetime import datetime
from rq import Queue, Worker
from rq_scheduler import Scheduler
from redis import Redis
from sqlalchemy import func, update
from typing import List
import json
import xxhash

from .models import db, Job, Tracker, Notification
from .tasks import JobRecord
from .sources import companies, LOCK_TIMEOUT

redis_conn = Redis()
task_queue = Queue(connection=redis_conn)
app = None

KEY_LOCK_COMPANIES_HASH_MAP = "lock:companies_hash_map"
KEY_COMPANIES_HASH_MAP = "companies_hash_map"

KEY_LOCK_SET_EXPIRED_TRACKERS = "lock:set_expired_trackers"
KEY_LOCK_FETCH_JOBS_FROM_COMPANIES = "lock:fetch_jobs_from_companies"

def init_app(flask_app):
    global app, redis_conn, task_queue
    app = flask_app
    redis_conn = Redis.from_url(app.config['REDIS_URL'])
    task_queue.connection = redis_conn


def clean_redis():
    redis_conn.delete(KEY_COMPANIES_HASH_MAP)
    redis_conn.delete(KEY_LOCK_COMPANIES_HASH_MAP)
    redis_conn.delete(KEY_LOCK_SET_EXPIRED_TRACKERS)
    redis_conn.delete(KEY_LOCK_FETCH_JOBS_FROM_COMPANIES)

def set_expired_trackers():
    # lock
    lock = redis_conn.lock(KEY_LOCK_SET_EXPIRED_TRACKERS, timeout=5)
    if not lock.acquire(blocking=False):
        return
    
    try:
        with app.app_context():
            expired_trackers = Tracker.query.filter(Tracker.is_removed == False, Tracker.is_expired == False, func.extract('epoch', func.now()) - func.extract('epoch', Tracker.date_created) > Tracker.duration).all()

            for tracker in expired_trackers:
                tracker.is_expired = True

                # send email by adding notification
                content = f'Tracker for keyword: {tracker.keyword} has expired! You still can view the jobs <a href="/#tracker/{tracker.secret}" target="_blank">here</a>'
                new_notification = Notification(token=tracker.token, email=tracker.email, content=content)
                db.session.add(new_notification)

            db.session.commit()

    finally:
        lock.release()


def calc_job_hash(company, title, description, location, date_posted_ts):
    # TODO: collision might happen, use better hash function
    data = f"{company} {title} {description} {location} {date_posted_ts}"
    h = xxhash.xxh32(data)
    # print(">>>>>", h.hexdigest(), data)
    return h.hexdigest(), h.intdigest()

def is_tracker_matched(keyword, company, title, description, location):
    return keyword.lower() in f"{company} {title} {description} {location}".lower()

def get_companies_hash_map():
    lock = redis_conn.lock(KEY_LOCK_COMPANIES_HASH_MAP, timeout=5)
    if not lock.acquire(blocking=True):
        return
    companies_hash_map = redis_conn.get(KEY_COMPANIES_HASH_MAP)
    lock.release()
    return json.loads(companies_hash_map)

def set_companies_hash_map(companies_hash_map, blocking=False):
    lock = redis_conn.lock(KEY_LOCK_COMPANIES_HASH_MAP, timeout=5)
    if not lock.acquire(blocking=blocking):
        return
    redis_conn.set(KEY_COMPANIES_HASH_MAP, json.dumps(companies_hash_map))
    lock.release()

def reload_companies_hash_map_from_db():
    with app.app_context():
        companies_hash_map = {}
        jobs = Job.query.filter(Job.is_removed == False).all()
        for job in jobs:
            date_posted_ts = int(job.date_posted.timestamp())
            h, h_int = calc_job_hash(job.company, job.title, job.description, job.location, date_posted_ts)

            if job.company not in companies_hash_map:
                companies_hash_map[job.company] = {
                    'jobs_hash_map': {},
                    'sum_hash': 0,
                }

            # to avoid duplicated hash, records
            if h not in companies_hash_map[job.company]['jobs_hash_map']:
                companies_hash_map[job.company]['jobs_hash_map'][h] = []

            companies_hash_map[job.company]['jobs_hash_map'][h].append(job.id)
            companies_hash_map[job.company]['sum_hash'] += h_int

        for company, j in companies_hash_map.items():
            print('=====', company, j['sum_hash'], set(j['jobs_hash_map']))
        
        set_companies_hash_map(companies_hash_map)
        print(companies_hash_map)

def sync_all_jobs(all_jobs):
    removed_job_ids = []
    new_jobs = {}

    current_companies_hash_map = get_companies_hash_map()
    # print('=====', current_companies_hash_map)
    is_changed = False
    for company, jobs in all_jobs.items():
        print("=" * 50, company, len(jobs))
        jobs: List[JobRecord]
        jobs_hash_map = {}
        sum_hash = 0
        for job in jobs:
            h, h_int = calc_job_hash(job.company, job.title, job.description, job.location, job.date_posted_ts)
            jobs_hash_map[h] = {
                'job': job,
            }
            sum_hash += h_int

        if company not in current_companies_hash_map:
            current_companies_hash_map[company] = {
                'sum_hash': sum_hash,
                'jobs_hash_map': {},
            }

            new_jobs.update(jobs_hash_map)
            # new_jobs = jobs_hash_map

            is_changed = True
        else:
            if current_companies_hash_map[company]['sum_hash'] != sum_hash:
                # now there are some new update

                # find the differences
                current_jobs_hash_set = set(current_companies_hash_map[company]['jobs_hash_map'])
                jobs_hash_set = set(jobs_hash_map)

                # print("===== CURRENT:", current_jobs_hash_set)
                # print("===== NEW:", jobs_hash_set)

                removed_jobs_hash_set = current_jobs_hash_set - jobs_hash_set
                new_jobs_hash_set = jobs_hash_set - current_jobs_hash_set

                for h in removed_jobs_hash_set:
                    removed_job_ids.extend(current_companies_hash_map[company]['jobs_hash_map'][h])
                    del current_companies_hash_map[company]['jobs_hash_map'][h]
                
                for h in new_jobs_hash_set:
                    new_jobs[h] = jobs_hash_map[h] 

                is_changed = True

    print("===== IS CHANGED:", is_changed)

    if not is_changed:
        return

    print("===== REMOVED:",removed_job_ids)
    print("===== NEW", new_jobs)

    with app.app_context():
        # update removed jobs
        stmt = (
            update(Job)
            .where(Job.id.in_(removed_job_ids))
            .values(is_removed=True, date_removed=db.func.now())
        )
        db.session.execute(stmt)

        trackers = Tracker.query.filter(Tracker.is_removed == False, Tracker.is_expired == False).all()
        trackers_new_jobs_map = {}

        # add new jobs and remap the id
        db_jobs = []
        for h, j in new_jobs.items():
            job = j["job"]
            db_job = Job(
                company=job.company,
                title=job.title,
                description=job.description,
                location=job.location,
                date_posted=datetime.fromtimestamp(job.date_posted_ts),
                link=job.link
            )
            j["db_job"] = db_job
            db_jobs.append(db_job)

        db.session.add_all(db_jobs)
        db.session.flush()

        for h, j in new_jobs.items():
            db_job_id = j["db_job"].id
            job = j["job"]

            # remap the id from db
            if h not in current_companies_hash_map[job.company]['jobs_hash_map']:
                current_companies_hash_map[job.company]['jobs_hash_map'][h] = []
            current_companies_hash_map[job.company]['jobs_hash_map'][h].append(db_job_id)

            for tracker in trackers:
                if is_tracker_matched(tracker.keyword, job.company, job.title, job.description, job.location):
                    # new job found for this tracker
                    if db_job_id not in trackers_new_jobs_map:
                        trackers_new_jobs_map[tracker.id] = {
                            'token': tracker.token,
                            'email': tracker.email,
                            'keyword': tracker.keyword,
                            'secret': tracker.secret,
                            'new_ids': []
                        }
                    trackers_new_jobs_map[tracker.id]['new_ids'].append(db_job_id)
        
        # update trackers
        for tracker_id, record in trackers_new_jobs_map.items():
            new_ids = record['new_ids']
            new_ids_str = ','.join(map(str, new_ids))
            stmt = (
                update(Tracker)
                .where(Tracker.id == tracker_id)
                .values(new_ids=new_ids_str)
            )
            db.session.execute(stmt)

            # send email by adding notification
            token = record['token']
            email = record['email']
            keyword = record['keyword']
            secret = record['secret']

            content = f'New jobs found for keyword: {keyword}, click this link <a href="/#tracker/{secret}" target="_blank">here</a> to view!'
            new_notification = Notification(token=token, email=email, content=content)
            db.session.add(new_notification)

        db.session.commit()

    set_companies_hash_map(current_companies_hash_map, True)


def fetch_jobs_from_companies():
    # lock
    lock = redis_conn.lock(KEY_LOCK_FETCH_JOBS_FROM_COMPANIES, timeout=LOCK_TIMEOUT)
    if not lock.acquire(blocking=False):
        return

    try:
        # for each company run fetch job
        tasks = {}
        for company in companies:
            task = task_queue.enqueue(company['func'], *company['args'])
            tasks[task] = company['name']

        while not all([task.is_finished for task in tasks]):
            time.sleep(1)

        # get results
        all_jobs = {}
        for task, company_name in tasks.items():
            print(task.return_value())
            status, jobs = task.return_value()

            if status: # True
                all_jobs[company_name] = jobs
            else:
                # timeout or request error
                ...

        sync_all_jobs(all_jobs)


    finally:
        lock.release()


def run_service():
    scheduler = Scheduler(
        connection=redis_conn,
        interval=1,
        queue=task_queue
    )

    def clean_all_jobs():
        clean_redis()
        # clean task_queue
        for job in task_queue.get_jobs():
            job.delete()
        # clean all scheduled jobs
        for job in scheduler.get_jobs():
            job.delete()

    clean_all_jobs()

    # create jobs snapshot from db
    reload_companies_hash_map_from_db()
    # TODO: run a scheduled task here

    # schedule fetch job
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=fetch_jobs_from_companies,
        interval=100,
        repeat=None
    )

    # schedule set_expired_trackers
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=set_expired_trackers,
        interval=100,
        repeat=None
    )

    scheduler.run()

    clean_all_jobs()


def run_worker():
    worker = Worker([task_queue], connection=redis_conn)
    worker.work(with_scheduler=True)
