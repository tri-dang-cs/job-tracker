import requests
from datetime import datetime

FETCH_TIMEOUT = 5

class JobRecord:
    def __init__(self, company, title, description, location, date_posted_ts, link):
        self.company = company
        self.title = title
        self.description = description
        self.location = location
        self.date_posted_ts = date_posted_ts
        self.link = link

def generic_fetch_jobs(url, company='sample', link_fmt='http://example.com/?id=%d', timeout=FETCH_TIMEOUT):
    # fetch from url with TIMEOUT
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 200:
            return False, f"status code: {response.status_code}"
            
        jobs = []
        for job in response.json()['data']:
            # convert dated_posted from isoformat to timestamp
            date_posted_ts = int(datetime.fromisoformat(job["date_posted"]).timestamp())
            jobs.append(JobRecord(
                company,
                job["title"],
                job["description"],
                job["location"],
                date_posted_ts,
                link_fmt % job["id"]
            ))

        return True, jobs
    except requests.exceptions.Timeout:
        return False, "timeout"
    except requests.exceptions.RequestException as e:
        return False, f"request error: {e}"

