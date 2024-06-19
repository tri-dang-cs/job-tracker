from .tasks import generic_fetch_jobs
import os

# companies = [
#     {
#         'name': 'google',
#         'func': generic_fetch_jobs,
#         'args': ['http://127.0.0.1:5001/api/jobs', 'google', 'http://127.0.0.1:5001/?id=%d'],
#         'link': 'http://127.0.0.1:5001/'
#     },
#     {
#         'name': 'facebook',
#         'func': generic_fetch_jobs,
#         'args': ['http://127.0.0.1:5002/api/jobs', 'facebook', 'http://127.0.0.1:5002/?id=%d'],
#         'link': 'http://127.0.0.1:5002/'
#     },
#     {
#         'name': 'microsoft',
#         'func': generic_fetch_jobs,
#         'args': ['http://127.0.0.1:5003/api/jobs', 'microsoft', 'http://127.0.0.1:5003/?id=%d'],
#         'link': 'http://127.0.0.1:5003/'
#     },
# ]

# LOCK_TIMEOUT = 5 * (3 + 1)

companies_str = os.environ.get("COMPANIES", "google,127.0.0.1:5001|facebook,127.0.0.1:5002|microsoft,127.0.0.1:5003")

companies = []
for company in companies_str.split("|"):
    parts = company.split(",")
    if len(parts) < 2: continue
    name, addr = parts[0], parts[1]
    if len(parts) > 2:
        pub_addr = parts[2]
    else:
        pub_addr = addr
    if pub_addr.lower().startswith("http") or pub_addr.lower().startswith("/"):
        pub_link = pub_addr
    else:
        pub_link = f"http://{pub_addr}"

    companies.append({
        'name': name,
        'func': generic_fetch_jobs,
        'args': [f'http://{addr}/api/jobs', name, f'{pub_link}/?id=%d'],
        'link': pub_link + '/',
    })

LOCK_TIMEOUT = 5 * (len(companies) + 1)